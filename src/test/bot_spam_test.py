from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Specify the relative path to the chromedriver (assuming it's in the same folder as your script)
chromedriver_path = './chromedriver'  # If your chromedriver is in the same folder

# Set up the service and webdriver
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Now you can use the driver for your automation tasks
driver.get("http://0.0.0.0:8000/islands/hub/forum/create/")

# Wait for the page to load
time.sleep(2)

# Fill out the title and text fields
driver.find_element(By.NAME, "title").send_keys("Test Title")  # Replace with the correct field name
driver.find_element(By.NAME, "text").send_keys("Test Text")  # Replace with the correct field name

# Submit the form (assuming the form's submit button is a button with type 'submit')
driver.find_element(By.XPATH, "//button[@type='submit']").click()

# Wait a bit to see what happens
time.sleep(3)

# Output the page source (in case you get redirected or an error message)
print(driver.page_source)

# Close the driver
driver.quit()
