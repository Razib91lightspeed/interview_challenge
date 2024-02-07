# Import necessary packages from Selenium
from selenium import webdriver  # Provides the WebDriver implementation for various browsers
from selenium.webdriver.common.by import By  # Allows locating elements using different strategies
from selenium.webdriver.common.keys import Keys  # Provides keys in the keyboard like RETURN, F1, ALT, etc.
from selenium.webdriver.support.ui import WebDriverWait  # Allows waiting for specific conditions before proceeding
from selenium.webdriver.support import expected_conditions as EC  # Provides a set of predefined conditions to wait for
import time  # Provides various time-related functions
import csv  # Provides functionality to read from and write to CSV files
import os  # Provides a way of using operating system-dependent functionality
import pytest  # A testing framework for writing and running Python tests

# Define a function to wait for the visibility of an element
def wait_for_element_visibility(driver, by, value, timeout=10):
    try:
        # WebDriverWait: Set up a wait with the given timeout and driver
        # until: Wait until the specified condition is true
        # EC.visibility_of_element_located: Condition to wait for an element to be visible
        return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)))
    except Exception as e:
        # Handle exceptions if the element is not found or visible within the specified timeout
        print(f"Error waiting for element with {by}: {value}")
        print(e)
        return None


# Open the Chrome browser
driver = webdriver.Chrome()

# Navigate to the Cargotec careers page
driver.get("https://www.cargotec.com/en/careers/")

# Handle cookie consent banner if present
try:
    # WebDriverWait: Set up a wait with a timeout of 5 seconds on the provided driver
    # until: Wait until the specified condition is true
    # EC.element_to_be_clickable: Condition to wait for an element to be clickable
    # (By.ID, "onetrust-accept-btn-handler"): Locator strategy to find the element by its ID
    cookie_consent_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
    )
    # Click the cookie consent button once it is clickable
    cookie_consent_button.click()
except Exception as e:
    # Handle exceptions if the cookie consent banner handling fails
    print("Error handling cookie consent banner")
    print(e)


# Wait for "Open positions" link to be clickable
open_positions_button = wait_for_element_visibility(driver, By.LINK_TEXT, "Open positions")

if open_positions_button:
    open_positions_button.click()

    # Wait for the page to load (Pauses the script's execution for 3 seconds.)
    time.sleep(3)

    # Switch to the new tab or window
    driver.switch_to.window(driver.window_handles[-1])

    # Locate the search boxes by class name
    keyword_search_box = wait_for_element_visibility(driver, By.CLASS_NAME, "keywordsearch-q")
    location_search_box = wait_for_element_visibility(driver, By.CLASS_NAME, "keywordsearch-locationsearch")

    if keyword_search_box and location_search_box:
        # Perform searches ('Trainee' and 'Tampere' desired search terms)
        keyword_search_box.send_keys("Trainee")
        location_search_box.send_keys("Tampere")

        # Press Enter to perform the search
        #keyword_search_box.send_keys(Keys.RETURN)
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

    pass

if __name__ == "__main__":
    pytest.main()
