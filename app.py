from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

app = Flask(__name__)

# Function to extract the download links
def get_download_links(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)

    try:
        # Navigate to the URL
        driver.get(f'https://teradownloader.com/download?link={url}')

        # Wait for the page to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Wait for 10 seconds
        time.sleep(10)

        # Define multiple selectors for the buttons
        selectors = [
            [
                (By.XPATH, "//html/body/section[1]/section[1]/div[3]/div[1]/div[2]/div/div/div/div/div/div/div[2]/a[2]"),
                (By.CSS_SELECTOR, "section:nth-of-type(1) a:nth-of-type(2)")
            ],
            [
                (By.XPATH, "//html/body/section[1]/section[1]/div[3]/div[1]/div[2]/div/div/div/div/div/div/div[2]/a[3]"),
                (By.CSS_SELECTOR, "section:nth-of-type(1) a:nth-of-type(3)")
            ],
            [
                (By.XPATH, "//html/body/section[1]/section[1]/div[3]/div[1]/div[2]/div/div/div/div/div/div/div[2]/a[4]"),
                (By.CSS_SELECTOR, "section:nth-of-type(1) a:nth-of-type(4)")
            ]
        ]

        # Initialize a dictionary to store the download links
        download_links = {}

        # Try to find the buttons using the provided selectors and extract the links
        for idx, selector_group in enumerate(selectors):
            button = None
            for by, selector in selector_group:
                try:
                    button = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    if button:
                        break
                except:
                    continue

            if button:
                download_link = button.get_attribute('href')
                if download_link:
                    download_links[f"response{idx + 1}"] = download_link
                else:
                    download_links[f"response{idx + 1}"] = "Button does not have a download link (href attribute)."
            else:
                download_links[f"response{idx + 1}"] = "Button not found."

        return download_links
    except Exception as e:
        return {"error": f"An error occurred: {e}"}
    finally:
        driver.quit()

@app.route('/download', methods=['GET'])
def download():
    link = request.args.get('link')
    if not link:
        return jsonify({"error": "Missing 'link' query parameter"}), 400
    
    download_links = get_download_links(link)
    return jsonify(download_links)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
