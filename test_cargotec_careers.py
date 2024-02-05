from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os
import pytest

def wait_for_element_visibility(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)))
    except Exception as e:
        print(f"Error waiting for element with {by}: {value}")
        print(e)
        return None

# Open the browser
driver = webdriver.Chrome()

# Navigate to the Cargotec careers page
driver.get("https://www.cargotec.com/en/careers/")

# Handle cookie consent banner if present
try:
    cookie_consent_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
    )
    cookie_consent_button.click()
except Exception as e:
    print("Error handling cookie consent banner")
    print(e)

# Wait for "Open positions" link to be clickable
open_positions_button = wait_for_element_visibility(driver, By.LINK_TEXT, "Open positions")

if open_positions_button:
    open_positions_button.click()

    # Wait for the page to load
    time.sleep(3)

    # Switch to the new tab or window
    driver.switch_to.window(driver.window_handles[-1])

    # Locate the search boxes by class name
    keyword_search_box = wait_for_element_visibility(driver, By.CLASS_NAME, "keywordsearch-q")
    location_search_box = wait_for_element_visibility(driver, By.CLASS_NAME, "keywordsearch-locationsearch")

    if keyword_search_box and location_search_box:
        # Perform searches ( 'Trainee' and 'Tampere' desired search terms)
        keyword_search_box.send_keys("Trainee")
        location_search_box.send_keys("Tampere")

        # Press Enter to perform the search
        location_search_box.send_keys(Keys.RETURN)

        # Wait for the search results to load
        wait_for_element_visibility(driver, By.CLASS_NAME, "searchResultsShell")

        # Get the job information
        job_elements = driver.find_elements(By.CLASS_NAME, "data-row")
        job_list = []

        for job_element in job_elements:
            # Extracting job title
            title_element = job_element.find_element(By.CSS_SELECTOR, "td.colTitle .jobTitle-link")
            title = title_element.text

            # Extracting department/business
            business = job_element.find_element(By.CSS_SELECTOR, "td.colDepartment .jobDepartment").text

            # Extracting job function
            job_function = job_element.find_element(By.CSS_SELECTOR, "td.colFacility .jobFacility").text

            # Extracting location
            location = job_element.find_element(By.CSS_SELECTOR, "td.colLocation .jobLocation").text

            job_info = {
                "Position Title": title,
                "Business": business,
                "Job Function": job_function,
                "Location": location
            }

            job_list.append(job_info)

            # Add debug prints
            print(f"Title: {title}, Business: {business}, Job Function: {job_function}, Location: {location}")

        # Delay before closing the browser
        time.sleep(5)

        # Handle cookie consent banner if present
        try:
            cookie_consent_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            driver.execute_script("arguments[0].click();", cookie_consent_button)
        except Exception as e:
            print("Error handling cookie consent banner")
            print(e)

        # Close the browser
        driver.quit()

        # Create the 'tests' directory if it doesn't exist
        tests_directory = "./tests"
        if not os.path.exists(tests_directory):
            os.makedirs(tests_directory)

        # Create and write to CSV file
        csv_file_path = os.path.join(tests_directory, "cargotec_trainee_positions.csv")
        header = ["Position Title", "Business", "Job Function", "Location"]

        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=header)

            # Write the header
            writer.writeheader()

            # Write job information
            for job_info in job_list:
                writer.writerow(job_info)

# Define a pytest test function
@pytest.mark.cargotec_test
def test_cargotec():
    # Add your test assertions here
    pass

if __name__ == "__main__":
    pytest.main()
