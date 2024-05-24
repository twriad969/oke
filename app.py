from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = '/app/.chrome-for-testing/chrome-linux64/chrome'

@app.route('/')
def extract_id_and_generate_response():
    link = request.args.get('link')
    if not link:
        return jsonify({'error': 'No link provided'})

    unique_id = link.split('/')[-1][1:]
    new_url = f"https://core.mdiskplay.com/box/terabox/video/{unique_id}.m3u8"

    try:
        with webdriver.Chrome(options=chrome_options) as driver:
            driver.set_page_load_timeout(7)  # Set a reasonable timeout
            driver.get(new_url)
            # Wait for the page to fully load
            driver.implicitly_wait(1)  # Adjust the wait time as needed

            # Check if the page is fully loaded
            if "404 Not Found" not in driver.title:
                response = {'response': new_url}
            else:
                response = {'error': 'Failed to load content'}

    except Exception as e:
        logger.error("An error occurred: %s", str(e))
        response = {'error': 'Failed to fetch content'}

    return jsonify(response)

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    # Running the app on the specified port
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
