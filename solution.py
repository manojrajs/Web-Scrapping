import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

# Set up Selenium WebDriver (we have to install the appropriate driver for your browser)
driver = webdriver.Chrome()

# Navigate to the webpage
driver.get("https://www.cermati.com/karir")

# Wait for the home page to load
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "navbar-link-wrapper")))

soup = BeautifulSoup(driver.page_source, "html.parser")
container = soup.findAll(class_="navbar-link-wrapper")
for index, data in enumerate(container):
    if index == 1:  # Check if it's the second iteration
        second_link = data.find(class_="navbar-link").get("href")
        break  # Exit the loop after finding the second link
jobs = "https://www.cermati.com/"+second_link
driver.get(jobs)

# Wait for the job listings page to load
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "page-job-wrapper")))

results = {}  # Dictionary to store the extracted data by department

while True:
    try:
        # Extract the data after it has loaded
        soup = BeautifulSoup(driver.page_source, "html.parser")
        container1 = soup.find(class_="page-job-wrapper")

        # Extract details from each job listing
        job_listings = container1.findAll(class_="page-job-list-wrapper")
        for listing in job_listings:
            department = listing.find(class_="job-detail margin-0 margin-right-20 sm").text.strip()

            # Extract href link from apply button
            button = listing.find(class_="btn btn-action btn-lg a-btn").get("href").split(" ")
            driver.get(button[0])

            # Wait for the new page to load
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "column.jobad-container")))

            # Extract data from the new page
            new_page_soup = BeautifulSoup(driver.page_source, "html.parser")
            container2 = new_page_soup.findAll(class_="column jobad-container wide-9of16 medium-5of8 print-block equal-column")

            # Process the extracted data
            for data in container2:
                location_element = data.find("span", class_="job-detail")
                location = location_element.find("spl-job-location")["formattedaddress"]
                title = data.find(class_="job-title").text.strip()
                description = data.find(itemprop="responsibilities").text.strip()
                qualification = data.find(itemprop="qualifications").text.strip()
                job_type = data.find(class_="job-details").text.strip()

                # Create a job dictionary
                job_data = {
                    "Title": title,
                    "Location": location,
                    "Description": description,
                    "Qualification": qualification,
                    "Job Type": job_type
                }

                # Add the job data to the corresponding department key in the results dictionary
                if department in results:
                    results[department].append(job_data)
                else:
                    results[department] = [job_data]

            # Go back to the job listing page
            driver.back()

        # Find the next button
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="career-jobs"]/div/div[6]/div/div[11]/div/button[9]')))

        if "disabled" in next_button.get_attribute("class"):
            break
        else:
            next_button.click()

    except TimeoutException:
        print("All pages scraped.")
        break

# Sort the results dictionary by department
sorted_results = dict(sorted(results.items()))

# Save the sorted results to a JSON file
with open("solution.json", "w") as f:
    json.dump(sorted_results, f, indent=4)

# Close the browser
driver.quit()




