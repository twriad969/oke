from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Function to create Chrome WebDriver with options
def create_webdriver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = '/app/.chrome-for-testing/chrome-linux64/chrome'
    return webdriver.Chrome(options=chrome_options)

@app.route('/')
def extract_id_and_generate_response():
    link = request.args.get('link')
    if not link:
        return jsonify({'error': 'No link provided'})

    unique_id = link.split('/')[-1][1:]
    new_url = f"https://core.mdiskplay.com/box/terabox/video/{unique_id}.m3u8"
    
    try:
        driver = create_webdriver()
        driver.get(new_url)
        time.sleep(5)

        if "404 Not Found" not in driver.title:
            response = {'response': new_url}
        else:
            response = {'error': 'Failed to load content'}
        
        logging.info(f"Processed link: {link}, response: {response}")
    except Exception as e:
        logging.error(f"Error processing link: {link}, error: {str(e)}")
        response = {'error': str(e)}
    finally:
        driver.quit()

    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port) 
