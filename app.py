from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os

app = Flask(__name__)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = '/app/.chrome-for-testing/chrome-linux64/chrome'

@app.route('/')
def open_link():
    # Get the link parameter from the URL
    link = request.args.get('link')
    if not link:
        return "No link provided", 400
    
    # Initialize the Chrome WebDriver using the provided binary location
    chrome_driver_path = ChromeDriverManager().install()
    driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)

    try:
        # Navigate to the specified URL
        driver.get(link)

        # Wait for a few seconds to allow the page to load
        driver.implicitly_wait(3)  # Adjust this time as needed
        
        # Get the current URL after the page has loaded
        current_url = driver.current_url

    finally:
        # Close the browser
        driver.quit()
        # Remove ChromeDriver log files to avoid cluttering Heroku's filesystem
        os.remove(chrome_driver_path)

    return f"Automation done. Current URL: {current_url}", 200

if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get('PORT', 5000)))
