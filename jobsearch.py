## Instructions
## 1. Download the Firefox driver and put it in the same directory as your script.
## 2. Make sure to have latest Python 3.x installed with pip
## 3. If you don't have selenium: `pip install selenium`

import requests
import os
import bs4
import csv
import json
import pprint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

driver = webdriver.Firefox()
# url to the page on amazon.jobs website showing the results of the search
url = 'https://amazon.jobs/en/search?offset=0&result_limit=10&sort=relevant&category%5B%5D=project-program-product-management-technical&job_type%5B%5D=Full-Time&cities%5B%5D=Seattle%2C%20Washington%2C%20USA&business_category%5B%5D=primevideo&distanceType=Mi&radius=24km&latitude=47.60358&longitude=-122.32945&loc_group_id=&loc_query=Seattle%2C%20WA%2C%20United%20States&base_query=&city=Seattle&country=USA&region=Washington&county=King&query_options=&'

## obtains all of the job posting links returned from search on amazon.jobs website and writes it to a txt file
## uses selenium webriver to open the page, collect all of the links and go to the next page until it reaches the last page
def jobLinks(url):
    driver.get(url)
    WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element_by_class_name('job-link'))
    jobLinksFile = open('joblinks.txt', 'w')

    #loop through all pages
    while True:
        #get all the links of the jobs presented on the page
        try:
            elem = driver.find_elements_by_class_name('job-link')
            print("Found some jobs!")
            # write each link to the opened txt file on a new line
            for el in elem:
                jobLink = el.get_attribute('href')
                jobLinksFile.write(jobLink+'\n')
        except:
            print("Did not find the element.")
        print('page completed')

        #find the button to go to the next page and break the loop if reached the last page of the search output
        try:
            rightButton = driver.find_element_by_class_name('right')
            # if the button is disabled, then break the loop (reached the last page)
            if 'disabled' in rightButton.get_attribute('class'):
                break
            # otherwise click the button to go to the next page
            rightButton.click()
        except:
            print("Right Button didn't work")
    
    # close the file
    jobLinksFile.close()
    # check - printing the list of links obtained
    jobLinksFile = open('joblinks.txt')
    content = jobLinksFile.read()
    jobLinksFile.close()
    print('Saved the following jobs:\n' + content)

## Takes a list of urls to description of each position
## Reads information about each position and saves it in csv file
def getJobDetails():
    # opening the file with urls
    joblinksFile = open('joblinks.txt')
    joblinks = joblinksFile.readlines()
    # defining the column names for csv file
    field_names = ['URL', 'JobID', 'Date', 'Location', 'Company', 
                    'Department', 'Level', 'Team', 'Title', 'Hiring Manager', 
                    'Title_Internal', 'Description (Short)', 'Status', 'Internal_Team Flag']
    # opening a new csv file in the append mode
    outputFile = open('jobs.csv', 'a', newline='')
    # opening a writer that writes as dictionary (allows column names)
    outputWriter = csv.DictWriter(outputFile, fieldnames = field_names)
    # writes headers of the file
    outputWriter.writeheader()

    # loop to get the details
    for line in joblinks:
        # break loop if reached the last line
        if line == "":
            break
        else:
            url = line
            # download the page
            print('Downloading the page %s' % url)
            # defining the proxy agent description in the post request to prevent web-site from blocking the request
            HEADERS = ({'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'})
            res = requests.get(url, headers=HEADERS)
            # check there is no error
            res.raise_for_status()
            # save html of the page in the BS4 parser
            
            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            #get Job attributes:

            # get title from the div with title class
            title = soup.select('.title')[0].getText()
            
            # get job ID from the div with ID class
            jobID = soup.select('.meta')[0].getText()
            
            # get location from the div showing location - using the CSS selector
            locationSelect = soup.select('#job-detail-body > div > div.col-12.col-md-5.col-lg-4.col-xl-3 > div > div:nth-child(1) > div.associations.col-12 > div:nth-child(1) > div > div > a')[0]
            location = locationSelect.get('aria-label')
            # slicing the location string to get rid of the word "Location" in the output
            location = location[9:]
            print(location)

            # get team name from the div showing the team - using the CSS selector (will get a wrong output if no team shown on the page)
            teamSelect = soup.select('#job-detail-body > div > div.col-12.col-md-5.col-lg-4.col-xl-3 > div > div:nth-child(1) > div.associations.col-12 > div:nth-child(2) > div > div > a')[0]
            team = teamSelect.get('aria-label')
            team = team[5:]

            #getting data from JSON stored in the html
            # get the properties of the div "Related Jobs"
            metaData = soup.select('#job-detail-body > div > div.col-12.col-md-5.col-lg-4.col-xl-3 > div > div:nth-child(3) > div')
            # get the value of the field containing JSON will all data about current job
            data_react_props = metaData[0]['data-react-props']
            # translate to JSON dictionary
            data_react_props_dict = json.loads(data_react_props)
            # get the values of the columns we're interested about the position
            datePosted = data_react_props_dict['currentJob']['date_posted']
            companyName = data_react_props_dict['currentJob']['company_name']
            department = data_react_props_dict['currentJob']['department']
            int_desc = data_react_props_dict['currentJob']['description_internal']
            desc_short = data_react_props_dict['currentJob']['description_short']
            level = data_react_props_dict['currentJob']['level']
            hiring_manager = data_react_props_dict['currentJob']['hiring_manager']
            id1 = data_react_props_dict['currentJob']['id']
            statuses = data_react_props_dict['currentJob']['job_statuses']
            title_internal = data_react_props_dict['currentJob']['title_internal']
            team1 = data_react_props_dict['currentJob']['team']
            # printing the output to see progress
            print(datePosted)
            print(department)
            print(title + '\n')

            #write it to the CSV file
            outputWriter.writerow(
                {
                'URL': url, 
                'Title': title, 
                'JobID': jobID, 
                'Location': location, 
                'Team': team, 
                'Date': datePosted, 
                'Company': companyName, 
                'Department': department, 
                'Level': level, 
                'Hiring Manager': hiring_manager, 
                'Title_Internal': title_internal, 
                'Description (Short)': desc_short, 
                'Status': statuses, 
                'Internal_Team Flag': team1
                    })

    outputFile.close()

# run both functions
jobLinks(url)
getJobDetails()