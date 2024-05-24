from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

app = Flask(__name__)

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = '/app/.chrome-for-testing/chrome-linux64/chrome'

# Function to create a new WebDriver instance
def create_webdriver():
    return webdriver.Chrome(options=chrome_options)

# Route for handling requests
@app.route('/')
def extract_id_and_generate_response():
    link = request.args.get('link')
    if not link:
        return jsonify({'error': 'No link provided'})

    try:
        # Create WebDriver instance
        driver = create_webdriver()

        # Extracting the unique ID from the link
        unique_id = link.split('/')[-1][1:]
        new_url = f"https://core.mdiskplay.com/box/terabox/video/{unique_id}.m3u8"

        # Load the page
        driver.get(new_url)

        # Wait for the page to load completely (adjust as needed)
        driver.implicitly_wait(10)

        # Checking if the page is fully loaded
        if "404 Not Found" not in driver.title:
            response = {'response': new_url}
        else:
            response = {'error': 'Failed to load content'}

    except Exception as e:
        response = {'error': str(e)}
    finally:
        # Close the WebDriver session
        if driver:
            driver.quit()

    return jsonify(response)

if __name__ == '__main__':
    # Get the port from the environment variable or use a default port
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
