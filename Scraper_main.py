#TO extract hospital name, speciality, street address, city, state, zipcode, phone number,


from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json
import pandas as pd
import time
import re
import caffeine

def parse_address(address):
    # Split the address into two parts: building name and the rest
    parts = address.split('\n', 1)

    # If the first part has a comma, assume there's no building name
    if ',' in parts[0]:
        building_name = None
        address_rest = parts[0]
    else:
        building_name = parts[0].strip()
        address_rest = parts[1] if len(parts) > 1 else ''

    # Regular expression to extract street address, city, state, and zip code
    address_pattern = r'(.+?),\s*([^,]+),\s*([A-Z]{2})\s*(\d{5})'
    match = re.search(address_pattern, address_rest)

    if match:
        street_address = match.group(1).strip()
        city = match.group(2).strip()
        state = match.group(3).strip()
        zipcode = match.group(4).strip()
    else:
        street_address = city = state = zipcode = None

    return building_name, street_address, city, state, zipcode

    #print("building: ", building_name, '\n street: ', street_address, '\ncity', city, '\nstate: ', state, '\nzipcode: ', zipcode)

driver = webdriver.Chrome()
def scrape(link):
    print(link)

    #class="error_error-content__title__O4eN3" error 404
    speciality = None
    #time.sleep(10)
    driver.get(link)
    title = driver.title
    driver.implicitly_wait(5)
    try:
        # Get the page's HTML content
        # Hospital Name and address.
        hospital_name_and_address = driver.find_element(By.XPATH,
                                                        "//*[@id='location']/div[1]/div[1]/div/div[1]/div[2]")
        s = hospital_name_and_address.text
        hospital_name, street_address, city, state, zipcode = parse_address(s)

        # print('address', address)
        # print('city', city)
        # print('state', state)
        # print('zipcode', zipcode)

        #print("\n NAME information")
        def get_name():
            fullName = driver.find_elements(By.CLASS_NAME, "doctors-single_name__vfOHL")
            fullName = fullName[0].text
            #print(fullName)
            list_Names = fullName.split(' ')
            #print(list_Names)
            middleName = None
        #print(list_Names)
            if len(list_Names) == 4:
                Prefix = list_Names[0][:-1]
                #print(Prefix)
                firstName = list_Names[1]
                #print(firstName)
                middleName = list_Names[2]
                #print(middleName)
                surName = list_Names[3]
                #print(surName)
            elif len(list_Names) == 3:
                Prefix = list_Names[0][:-1]
                firstName = list_Names[1]
                surName = list_Names[2]
            else:
                firstName = list_Names[1]
                surName = list_Names[-1]


            return firstName, middleName, surName

        firstName, middleName, surName = get_name()
        # print("Prefix: ", Prefix)
        # print("First name: ", firstName)
        # print("Middle Name: ", middleName)
        # print("Last name: ", surName)
        # print("\n")

        # Biography
        biography = driver.find_element(By.CLASS_NAME, "DoctorProfileOverview_biography__fMwpJ")
        # print("Biography: ", biography.text)
        biography = biography.text

        # Insurance class="DoctorInsurance_accepted__orxVP"
        insuranceList = driver.find_elements(By.CLASS_NAME, "DoctorInsurance_accepted__orxVP")
        insuranceList_converted = []
       # print('Insurances Accepted')
        for i in insuranceList:
           # print(i.text)
            insuranceList_converted.append(i.text)

        #print(insuranceList_converted)

        # Other locations class="LocationAccordion_locations__values__U3hjw"
        locationList = driver.find_elements(By.CLASS_NAME,
                                            "LocationAccordion_locations__values__U3hjw")
        # print(len(locationList))
        locationList_converted = []
        for i in locationList:
            # print(i.text)
            locationList_converted.append(i.text)

        # print(locationList_converted)

        def clean_address_list(address_list):
            # Initialize an empty list to store cleaned addresses
            cleaned_list = []

            # Iterate over the provided list
            for i in range(0, len(address_list), 2):
                # Extract the address and phone number entries
                address = address_list[i]
                # Clean up and format the address
                address_cleaned = address.strip()
                address_cleaned = address.strip().replace('\n', ' ')
                # Append the cleaned address to the list
                cleaned_list.append(address_cleaned)
            return cleaned_list

        locationList_converted = clean_address_list(locationList_converted)
        # print(locationList_converted)

        otherLocations = locationList_converted

        # Get number of clinical trials class="DoctorProfileClinicalResearch_text__eJIbe"
        try:
            trialsNum = driver.find_element(By.CLASS_NAME, "DoctorProfileClinicalResearch_text__eJIbe")
        # print("Number of Clinical Trials: ", trialsNum.text)
            numTrials = trialsNum.text
        except:
            numTrials = "Not Found"

        try:
            # acceptances Card_body__metadata__4bfhr
            acceptance = driver.find_elements(By.CLASS_NAME, "Card_body__metadata__4bfhr")
            # print(len(acceptance))

            boolAcceptance = False
            if 'Recruiting' in acceptance[0].text.split(' '):
                boolAcceptance = True

            if boolAcceptance:
                boolAcceptance = 'Yes'
            else:
                boolAcceptance = 'No'
            # print(boolAcceptance)
        except:
            boolAcceptance = 'Not Found'

        def get_x(x):
            first_class_elements = driver.find_elements(By.CLASS_NAME,
                                                        'DoctorProfileOverview_credentials__header__FxZpf')
            for element in first_class_elements:
                # print(element.text)
                if element.text == x:
                    # Find the following sibling element with the second class
                    second_class_element = element.find_element(By.XPATH,
                                                                'following-sibling::div[@class="DoctorProfileOverview_credentials__credential-item__3-6BO"]')

                    # Do something with the second class element, e.g., print the text
                    return second_class_element.text

        def get_x_multiple(x):
            first_class_elements = driver.find_elements(By.CLASS_NAME,
                                                        'DoctorProfileOverview_credentials__header__FxZpf')
            for element in first_class_elements:
                # print(element.text)
                if element.text == x:
                    # Find the following sibling element with the second class
                    second_class_elements = element.find_elements(By.XPATH,
                                                                  'following-sibling::div[@class="DoctorProfileOverview_credentials__credential-item__3-6BO"]')

                    # Do something with the second class element, e.g., print the text
                    text = [i.text for i in second_class_elements]
                    return text
            return ""

        licences = get_x('Licenses')
        gender = get_x('Gender')
        language = get_x_multiple('Languages Spoken')
        speciality = get_x_multiple('Specialties')

    except Exception as e:
        print(f"An error occurred: {e}")

    #driver.quit()
    # print(language)
    # print(licences)
    # print(gender)
    # print(speciality)


    # print([[hospital_name] ,[address], [city], [state], [zipcode], [spec], ])
    return [[hospital_name] ,[street_address], [city], [state], [zipcode], [speciality], [firstName], [middleName], [surName],[gender], [biography], [insuranceList_converted], [licences], [numTrials], [boolAcceptance], [locationList_converted], [link]]



def create_initial_dataframe(data):
    # Transpose the data to align columns correctly
    transposed_data = list(map(list, zip(*data)))

    # Create a DataFrame with appropriate column names
    df = pd.DataFrame(transposed_data, columns = ['Hospital Name', 'Address', 'City', 'State', 'Zip Code', 'Speciality', 'first_name', 'middle_name', 'last_name','gender' , 'description', 'Insurance', 'Licenses', 'Number of Trials', 'Actively recruiting Status', 'Other Locations', 'website'])
    # Add a Serial Number column starting from 1
    df.insert(0, 'Serial Number', range(1, len(df) + 1))
    return df
#  ['Hospital Name', 'Address', 'City', 'State', 'Zip Code', 'Speciality', 'first_name', 'middle_name', 'last_name','gender' , 'description', 'Insurance', 'Licenses', 'Number of Trials', 'Actively recruiting Status', 'Other Locations', 'website'])

def add_data_to_dataframe(df, new_data):
    # Transpose new data to align columns correctly
    transposed_new_data = list(map(list, zip(*new_data)))

    # Create a new DataFrame for the new data
    new_df = pd.DataFrame(transposed_new_data, columns=['Hospital Name', 'Address', 'City', 'State', 'Zip Code', 'Speciality', 'first_name', 'middle_name', 'last_name','gender' , 'description', 'Insurance', 'Licenses', 'Number of Trials', 'Actively recruiting Status', 'Other Locations', 'website'])

    # Add a Serial Number column for new data
    new_df.insert(0, 'Serial Number', range(len(df) + 1, len(df) + len(new_df) + 1))

    # Append the new DataFrame to the existing one
    df = pd.concat([df, new_df], ignore_index=True)

    return df


def excel_reader():
    df = pd.read_excel('medidata.xlsx')

    # Iterate over each row and yield the specific column value
    for value in df['website']:
        yield value
value_generator = excel_reader()

def run():
    #get link
    output_file = 'scraped_file.xlsx'
    for i in range(0,2000):
        link = next(value_generator)
        #scrape

        try:
            data = scrape(link)
            if i == 0:
                df = create_initial_dataframe(data)
            else:
                df = add_data_to_dataframe(df, data)
        except Exception as e:
            print(f"An error occurred: {e}")
            df.to_excel(output_file, index = False)


    df.to_excel(output_file, index = False)
    driver.quit()
    print("Finished")
run()




