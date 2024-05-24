from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import asyncio

app = Flask(__name__)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = '/app/.chrome-for-testing/chrome-linux64/chrome'

async def check_content(new_url):
    try:
        with webdriver.Chrome(options=chrome_options) as driver:
            driver.get(new_url)
            # Wait for the page to fully load (you can adjust the wait time as needed)
            await asyncio.sleep(2)

            # Check if the page is fully loaded
            if "404 Not Found" not in driver.title:
                return {'response': new_url}
            else:
                return {'error': 'Failed to load content'}
    except Exception as e:
        # Handle any exceptions here
        return {'error': str(e)}

@app.route('/')
def extract_id_and_generate_response():
    link = request.args.get('link')
    if not link:
        return jsonify({'error': 'No link provided'})

    unique_id = link.split('/')[-1][1:]
    new_url = f"https://core.mdiskplay.com/box/terabox/video/{unique_id}.m3u8"

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(check_content(new_url))
    loop.close()

    return jsonify(result)

if __name__ == '__main__':
    # Running the app on the specified port
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
