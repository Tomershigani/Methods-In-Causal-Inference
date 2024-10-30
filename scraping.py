import ast

import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time


def unify_xls_files(folder_path):
    """
    This function takes a folder path as input, reads all xls files in the folder,
    and returns a unified DataFrame.

    Args:
      folder_path: The path to the folder containing the xls files.

    Returns:
      A pandas DataFrame containing the unified data.
    """
    all_dataframes = []
    print(os.listdir(folder_path))
    for filename in os.listdir(folder_path):
        if filename.endswith(".xls"):
            file_path = os.path.join(folder_path, filename)
            try:
                df = pd.read_html(file_path)
                df = pd.DataFrame(df[0])  # Assuming the first table is the relevant one
                all_dataframes.append(df)
            except Exception as e:
                print(f"Error reading file {filename}: {e}")

    if not all_dataframes:
        print("No xls files found in the specified folder.")
        return None

    unified_df = pd.concat(all_dataframes, ignore_index=True)
    return unified_df


def get_single_adress(df):
    # Initialize the WebDriver
    driver = webdriver.Chrome()
    driver.get("https://www.gov.il/apps/mapi/parcel_address/parcel_address.html")
    for i in range(len(df)):
        try:
            # Open the website
            print(f" scraping {df['policy_number'][i]}")
            gush, helka = df['policy_number'][i]
            print(gush, helka)
            # Wait for the page to load completely
            WebDriverWait(driver, 8).until(
                EC.visibility_of_element_located((By.XPATH, "//div[@id='cbx_lotparcel']"))
            )

            # Locate the parent div that contains the radio button and click it using JavaScript
            radio_button_container = driver.find_element(By.XPATH, "//div[@id='cbx_lotparcel']")

            # Scroll the parent element into view if necessary
            driver.execute_script("arguments[0].scrollIntoView(true);", radio_button_container)

            # Force a click on the parent element using JavaScript
            driver.execute_script("arguments[0].click();", radio_button_container)
            time.sleep(1)

            # Alternatively, locate the radio button directly and click using JavaScript
            radio_button = driver.find_element(By.XPATH, "//input[@value='lotparcel_radio']")
            driver.execute_script("arguments[0].click();", radio_button)
            time.sleep(1)

            first_input = driver.find_element(By.XPATH,
                                              '/html/body/div[3]/div/div[4]/div[2]/div/div[1]/div/div[1]/input')
            if first_input.get_attribute('value') != "":
                first_input.clear()  # Clear the input if it's not empty
            first_input.send_keys(gush)

            # Enter the second input
            second_input = driver.find_element(By.XPATH,
                                               '/html/body/div[3]/div/div[4]/div[2]/div/div[1]/div/div[2]/input')
            if second_input.get_attribute('value') != "":
                second_input.clear()  # Clear the input if it's not empty
            second_input.send_keys(helka)

            # Click the submit button
            submit_button = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[5]/div/button')
            submit_button.click()
            time.sleep(1)

            WebDriverWait(driver, 8).until(
                EC.visibility_of_element_located((By.ID, 'AddrResults'))
            )

            # Locate the ul element containing the addresses
            address_list_ul = driver.find_element(By.ID, 'addr_ul')

            # Find all the li elements within the ul
            address_items = address_list_ul.find_elements(By.TAG_NAME, 'li')

            # Extract the text of each li element and store it in a list
            address_items = [item.text for item in address_items]
            print(address_items)
            # Output the list of addresses
            addresses.append(address_items)
        except:

            print(f'problem with {gush, helka}')
            addresses.append(["Error " + str(gush) + str(helka)])
        finally:
            # Optionally, wait to see the result and then close the browser
            WebDriverWait(driver, 5)
    driver.quit()


df = unify_xls_files('C:/Users/EinamCastel/PycharmProjects/inference/')
print(df)
df = df.drop_duplicates()

# Rename columns
df = df.rename(columns={
    'גוש חלקה': 'policy_number',
    'יום מכירה': 'sale_date',
    'תמורה מוצרהת בש"ח': 'product_value_this_year',
    'שוי מכירה בש"ח': 'sale_value_this_year',
    'מהות': 'nature',
    'חלק נמכר': 'percentage_of_sale',
    'ישוב': 'city',
    'שנת בניה': 'year_of_construction',
    'שטח': 'area',
    'חדרים': 'bedrooms',
    'עדיפות': 'priority'
})

df['policy_number'] = df['policy_number'].str.split('-').apply(lambda x: x[:2])
df.to_excel('real_estate_df_21_sep.xlsx', index_label=False)


df = pd.read_excel('real_estate_df_21_sep.xlsx')
# df['policy_number'] = df['policy_number'].apply(ast.literal_eval)
addresses = []
get_single_adress(df)

df['addresses'] = addresses
print(df)
df.to_excel('df with addresses.xlsx', index=False)
