from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

app = Flask(__name__)

chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (without UI)
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration

# Configure Chrome to run in Heroku
chrome_options.binary_location = '/app/.apt/usr/bin/google-chrome'
chrome_options.add_argument("--no-sandbox")

# Keep a single instance of the WebDriver for efficiency
driver = None

def get_driver():
    global driver
    if driver is None:
        driver = webdriver.Chrome(options=chrome_options)
    return driver

@app.route('/api/extract', methods=['GET'])
def extract_id_and_generate_response():
    link = request.args.get('link')
    if not link:
        return jsonify({'error': 'No link provided'})

    # Extracting the unique ID from the link
    unique_id = link.split('/')[-1][1:]  # Extracting the ID as before

    # Constructing the new URL based on the extracted ID
    new_url = f"https://core.mdiskplay.com/box/terabox/video/{unique_id}.m3u8"

    try:
        # Using the WebDriver instance
        driver = get_driver()

        # Loading the page
        driver.get(new_url)

        # Waiting for the page to load completely
        driver.implicitly_wait(10)  # Adjust the wait time as needed

        # Checking if the page is fully loaded
        if "404 Not Found" not in driver.title:  # Checking for a common indication that the page is not fully loaded
            return jsonify({'response': new_url})
        else:
            return jsonify({'error': 'Failed to load content'})

    except Exception as e:
        # Log the error for debugging
        print(f"An error occurred: {str(e)}")
        return jsonify({'error': 'An error occurred while processing the request'})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
