from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Selenium options
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--window-size=1920,1080")

# Rotate User-Agent
ua = UserAgent()
options.add_argument(f"user-agent={ua.random}")

# Set up ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

url = "https://www.ebay.com/globaldeals/tech"

def scrape_products():
    driver.get(url)
    wait = WebDriverWait(driver, 15)

    try:
        # Wait until the product tiles are visible
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "dne-itemtile")))

        products = driver.find_elements(By.CLASS_NAME, "dne-itemtile")
        product_list = []

        for product in products:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                title = product.find_element(By.CSS_SELECTOR, "h3").text
            except:
                title = "N/A"

            try:
                price = product.find_element(By.CLASS_NAME, "first").text
            except:
                price = "N/A"

            try:
                original_price = product.find_element(By.CLASS_NAME, "itemtile-price-strikethrough").text
            except:
                original_price = "N/A"

            try:
                shipping = product.find_element(By.CLASS_NAME, "dne-itemtile-delivery").text
            except:
                shipping = "N/A"

            try:
                item_url = product.find_element(By.XPATH, ".//a[@itemprop='url']").get_attribute("href")
            except:
                item_url = "N/A"

            product_data = {
                "timestamp": timestamp,
                "title": title,
                "new_price": price,
                "original_price": original_price,
                "shipping_info": shipping,
                "item_url": item_url
            }

            product_list.append(product_data)

        return product_list

    except Exception as e:
        print("Error occurred:", e)
        return None

def save_to_csv(data):
    file_name = "ebay_tech_deals.csv"
    try:
        df = pd.read_csv(file_name)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["timestamp", "title", "new_price", "original_price", "shipping_info", "item_url"])

    new_df = pd.DataFrame(data)
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(file_name, index=False)

if __name__ == "__main__":
    print("Scraping Product Data...")
    scraped_data = scrape_products()

    if scraped_data:
        save_to_csv(scraped_data)
        print("Data saved to ebay_tech_deals.csv")
    else:
        print("Failed to scrape data.")

    driver.quit()
