import json
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
import os
import time

app = Flask(__name__)

# Load cookies from cookies.json file
def load_cookies_from_file(filename):
    with open(filename, 'r') as f:
        cookies = json.load(f)
    return cookies

# Function to execute Selenium script and return the download link
def get_download_link(link, cookies_file):
    # Configure ChromeOptions for headless mode
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    # Load cookies from file
    cookies = load_cookies_from_file(cookies_file)

    # Initialize the WebDriver with loaded cookies
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.get("https://mdiskplay.com/")

    # Add cookies to the browser session
    for cookie in cookies:
        driver.add_cookie(cookie)

    # Navigate to the website
    driver.get("https://mdiskplay.com/")

    # Check if the link parameter is provided in the request
    if link:
        # Click the input field to paste the link
        input_field = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div/div/main/div[2]/div/div[2]/div/input')
        input_field.click()
    
        # Enter the provided URL
        input_field.send_keys(link)
        time.sleep(1)  # Wait for the input to be processed
    
        # Click the 'GET LINK' button
        get_link_button = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div/div/main/div[2]/div/div[2]/div/div')
        get_link_button.click()
    
    # Wait for the download button to be clickable and then click it
    download_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "premiumDownloadVideo_downloadButton")]'))
    )
    download_button.click()
    
    # Wait for 20 seconds
    time.sleep(20)
    
    # After 10 seconds, construct the download link
    time.sleep(10)
    current_url = driver.current_url
    parsed_url = urlparse(current_url)
    path_parts = parsed_url.path.split('/')
    desired_string = path_parts[-1] if path_parts[-1] else path_parts[-2]  # Get the last non-empty part of the path
    download_link = f"https://download.mdiskplay.com/video/{desired_string}.mp4"
    
    # Close the WebDriver
    driver.quit()
    
    return download_link

@app.route('/')
def index():
    # Get the link parameter from the request
    link = request.args.get('link')
    
    # Path to cookies file
    cookies_file = 'cookies.json'
    
    # Execute Selenium script to get the download link
    download_link = get_download_link(link, cookies_file)
    
    # Return the response as JSON
    return jsonify({"download_link": download_link})

if __name__ == '__main__':
    # Heroku sets PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
