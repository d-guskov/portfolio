from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import pandas as pd
import datetime
import time
import csv

def round_up(number): return int(number) + (number % 1 > 0)

def scrape_data(date, url, driver):
    driver.get(url)
    time.sleep(3)
    
    date_picker_from = driver.find_element(By.ID, "frm_suche:ldi_datumVon:datumHtml5")
    date_picker_to = driver.find_element(By.ID, "frm_suche:ldi_datumBis:datumHtml5")

    date_picker_from.clear()
    date_picker_from.send_keys(date)

    date_picker_to.clear()
    date_picker_to.send_keys(date)
    date_picker_from.send_keys(Keys.ENTER)

    content = driver.page_source
    soup = BeautifulSoup(content, "html.parser")
    datas = []
    for i in soup.find_all('table'):
        datas.append(i.text)
    try:
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
    start_date_input = input("Enter the start date (YYYY-MM-DD): ")
    end_date_input = input("Enter the end date (YYYY-MM-DD): ")
    start_date = datetime.datetime.strptime(start_date_input, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date_input, "%Y-%m-%d").date()

    diff = end_date - start_date

    url = "https://neu.insolvenzbekanntmachungen.de/ap/suche.jsf"
    dataframes = []
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager("114.0.5735.90").install()))

    for i in range(diff.days + 1):
        date = (start_date + datetime.timedelta(days=i)).strftime("%d.%m.%Y")
        scrape_data(date, url, driver)
    
    driver.quit()

    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
        combined_df.to_csv('insolvenz_data.csv', 
                           index=False, header=False, mode='w', sep=',')
        print("Dataframes saved to CSV file.")
    else:
        print("No dataframes to save.")

