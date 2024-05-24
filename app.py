from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

app = Flask(__name__)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = '/app/.chrome-for-testing/chrome-linux64/chrome'

driver = webdriver.Chrome(options=chrome_options)

@app.route('/')
def extract_id_and_generate_response():
    link = request.args.get('link')
    if not link:
        return jsonify({'error': 'No link provided'})

    unique_id = link.split('/')[-1][1:]
    new_url = f"https://core.mdiskplay.com/box/terabox/video/{unique_id}.m3u8"

    try:
        driver.get(new_url)
        # Wait for the page to fully load (you can adjust the wait time as needed)
        time.sleep(5)

        # Check if the page is fully loaded
        if "404 Not Found" not in driver.title:
            response = {'response': new_url}
        else:
            response = {'error': 'Failed to load content'}

    finally:
        # Close the browser
        driver.quit()

    return jsonify(response)

if __name__ == '__main__':
    # Running the app on the specified port
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
