import csv
import time
import datetime
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

# Function to scrape data from a given date
def scrape_data(date, url, driver):
    driver.get(url)
    time.sleep(3)
    
    # Find date picker elements on the page
    date_picker_from = driver.find_element(By.ID, "frm_suche:ldi_datumVon:datumHtml5")
    date_picker_to = driver.find_element(By.ID, "frm_suche:ldi_datumBis:datumHtml5")

    # Clear date pickers and enter the desired date
    date_picker_from.clear()
    date_picker_from.send_keys(date)

    date_picker_to.clear()
    date_picker_to.send_keys(date)
    date_picker_from.send_keys(Keys.ENTER)

    # Get the page source and create a BeautifulSoup object
    content = driver.page_source
    soup = BeautifulSoup(content, "html.parser")
    datas = []
    
    # Extract table data and store in the datas list
    for i in soup.find_all('table'):
        datas.append(i.text)
    
    try:
        # Split and process the data for the given date
        people = datas[1].split(date)
        people = people[1:]
        df = pd.DataFrame(people, columns=[date])
        df1 = df[date].str.split("\n", n=5, expand=True)
        df1["Date"] = date
        dataframes.append(df1)
    except:
        print("No insolvencies on this day: " + date)
    time.sleep(10)

if __name__ == "__main__":
    # Get user input for start and end dates
    start_date_input = input("Enter the start date (YYYY-MM-DD): ")
    end_date_input = input("Enter the end date (YYYY-MM-DD): ")
    start_date = datetime.datetime.strptime(start_date_input, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date_input, "%Y-%m-%d").date()

    # Calculate the date range
    diff = end_date - start_date

    url = "https://neu.insolvenzbekanntmachungen.de/ap/suche.jsf"
    dataframes = []
    
    # Set up the Chrome webdriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Loop through each day in the date range and scrape data
    for i in range(diff.days + 1):
        date = (start_date + datetime.timedelta(days=i)).strftime("%d.%m.%Y")
        scrape_data(date, url, driver)
    
    # Quit the driver
    driver.quit()

    # If dataframes were collected, combine and save them to a CSV file
    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
        combined_df.to_csv('insolvenz_data.csv', 
                           index=False, header=False, mode='w', sep=',')
        print("Dataframes saved to CSV file.")
    else:
        print("No dataframes to save.")
