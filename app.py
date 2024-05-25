from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)

def process_link(link):
    if not link:
        return None

    try:
        unique_id = link.split('/')[-1][1:]  # Extract unique ID and remove the first character
        modified_link = f"https://mdiskplay.com/terabox/{unique_id}"

        # Set up Selenium options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = '/app/.chrome-for-testing/chrome-linux64/chrome'
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)

        # Open the modified link
        driver.get(modified_link)

        # Wait for the page to fully load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Wait for an additional 3 seconds to ensure all elements are loaded
        time.sleep(5)
        
        driver.quit()

        return f"https://core.mdiskplay.com/box/terabox/video/{unique_id}.m3u8"
    except Exception as e:
        print(f"An error occurred: {e}")
        if 'driver' in locals():
            driver.quit()
        return None

@app.route('/')
def index():
    link = request.args.get('link')
    if not link:
        return jsonify({"status": "error", "message": "No link provided"})

    modified_link = process_link(link)
    if modified_link:
        return jsonify({"status": "done", "url": modified_link})
    else:
        return jsonify({"status": "error", "message": "Failed to process link"})

if __name__ == '__main__':
    app.run(debug=True)
