from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

app = Flask(__name__)

# Function to execute Selenium script and return the download link
def get_download_link(link):
    # Configure ChromeOptions
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = '/app/.chrome-for-testing/chrome-linux64/chrome'
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the WebDriver with specified Chrome binary location
    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to the website
    driver.get("https://mdiskplay.com/")

    # Check if the link parameter is provided
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
    download_link = current_url
    
    # No need to close the WebDriver for browser visibility
    
    return download_link

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        link = request.form['link']
        
        # Execute Selenium script to get the download link
        download_link = get_download_link(link)
        
        # Return the response as JSON
        return jsonify({"download_link": download_link})
    else:
        return render_template('index.html')

if __name__ == '__main__':
    # Heroku sets PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
