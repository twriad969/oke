import os
from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

@app.route('/')
def open_link():
    # Get the link parameter from the URL
    link = request.args.get('link')
    if not link:
        return "No link provided", 400
    
    # Specify Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = '/app/.chrome-for-testing/chrome-linux64/chrome'
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Navigate to the specified URL
        driver.get(link)
        
        # Wait for a few seconds to allow the page to load
        time.sleep(5)  # Adjust this time as needed
        
        # Get the current URL after the page has loaded
        current_url = driver.current_url

    finally:
        # Close the browser
        driver.quit()

    return f"Automation done. Current URL: {current_url}", 200

if __name__ == '__main__':
    # Use the dynamic port assigned by Heroku
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
