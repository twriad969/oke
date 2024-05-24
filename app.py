from flask import Flask, request
from selenium import webdriver

app = Flask(__name__)

# Function to open URL in headless browser and close it
def open_browser(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = '/app/.chrome-for-testing/chrome-linux64/chrome'
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        # Add any additional logic here
    finally:
        driver.quit()

@app.route('/')
def open_url():
    url = request.args.get('url')
    if url:
        open_browser(url)
        return "URL opened successfully!"
    else:
        return "No URL provided!"

if __name__ == '__main__':
    app.run(debug=True)
