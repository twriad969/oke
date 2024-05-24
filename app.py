from flask import Flask
from selenium import webdriver

app = Flask(__name__)

@app.route('/')
def open_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.example.com")  # Replace with your URL
    driver.quit()
    return "Browser opened and closed successfully!"

if __name__ == '__main__':
    app.run(debug=True)
