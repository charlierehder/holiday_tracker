from datetime import datetime, date
import json
from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
from typing import List


# -------------------------------------------
# Modify the holiday class to 
# 1. Only accept Datetime objects for date.
# 2. You may need to add additional functions
# 3. You may drop the init if you are using @dataclasses
# --------------------------------------------
@dataclass
class Holiday:
    name: str
    date: datetime
    
    def __str__ (self):
         return self.name + ' (' + str(self.date) + ')' 
           
# -------------------------------------------
# The HolidayList class acts as a wrapper and container
# For the list of holidays
# Each method has pseudo-code instructions
# --------------------------------------------
@dataclass
class HolidayList:
    innerHolidays: List[Holiday]
   
    def addHoliday(self, holidayObj):
        # Make sure holidayObj is an Holiday Object by checking the type
        # Use innerHolidays.append(holidayObj) to add holiday
        # print to the user that you added a holiday
        if type(holidayObj) is Holiday:
            self.innerHolidays.append(holidayObj)
            print(str(holidayObj) + ' has been added to the holiday list')
        else:
            print('Error')
            print('Your holiday was not added to the list')

    def findHoliday(self, HolidayName, Date):
        # Find Holiday in innerHolidays
        for holiday in self.innerHolidays:
            if holiday.name == HolidayName and holiday.date == Date:
                return holiday
        return None

    def removeHoliday(self, HolidayName, Date):
        # Find Holiday in innerHolidays by searching the name and date combination.
        # remove the Holiday from innerHolidays
        # inform user you deleted the holiday
        self.innerHolidays.remove(self.findHoliday(HolidayName, Date)) 

    def read_json(self, filepath):
        # Read in things from json file location
        # Use addHoliday function to add holidays to inner list.
        print("Seeding list with initial json...")
        with open(filepath, 'r') as f:
            holidays = json.load(f)

        for holiday in holidays['holidays']:
            datetime_obj = datetime.strptime(holiday['date'], '%Y-%m-%d').date()
            self.addHoliday(Holiday(holiday['name'], datetime_obj))

        print("Complete")

    def save_to_json(self, filelocation):
        # Write out json file to selected file. 
        with open(filelocation, "w") as f:
            json_dict = { 'holidays' : [hol.__dict__ for hol in self.innerHolidays] }
            json.dump(json_dict, f, default=str)
        print('List Saved')
        
    def scrapeHolidays(self):
        # Scrape Holidays from https://www.timeanddate.com/holidays/us/ 
        # Remember, 2 previous years, current year, and 2  years into the future. You can scrape multiple years by adding year to the timeanddate URL. For example https://www.timeanddate.com/holidays/us/2022
        # Check to see if name and date of holiday is in innerHolidays array
        # Add non-duplicates to innerHolidays
        # Handle any exceptions.   

        print("Scraping timeanddate.com for all holidays from 2020 - 2024")
        years = ['2020', '2021', '2022', '2023', '2024']

        for year in years:
            try:
                url = 'https://www.timeanddate.com/holidays/us/' + year
                response_html = requests.get(url).text
                soup = BeautifulSoup(response_html, 'html.parser')

                # ISOLATING DATA TABLE IN HTML
                table = soup.find('table', attrs={'id':'holidays-table'})

                # ITERATE THROUGH EACH ROW IN THE TABLE AND STORE DATA
                # IN A DICTIONARY
                for row in table.tbody.find_all('tr'): # get's all html rows and makes them iterable
                    data = row.find_all('td') # row data 
                    if len(data) >= 4: 
                        name = data[1].string
                        date = row.find('th').string + ', ' + year
                        try:
                            datetime_obj = datetime.strptime(date, '%b %d, %Y').date()
                            self.addHoliday(Holiday(name, datetime_obj)) 
                        except ValueError:
                            print("Skipping invalid date")
            except:
                print("Something went wrong while parsing")
                print("Skipping page")


    def numHolidays(self):
        # Return the total number of holidays in innerHolidays
        return len(self.innerHolidays)
    
    def filter_holidays_by_week(self, year, week_number):
        # Use a Lambda function to filter by week number and save this as holidays, use the filter on innerHolidays
        # Week number is part of the the Datetime object
        # Cast filter results as list
        # return your holidays
        filtered_holidays = filter(lambda x: x.date.isocalendar()[1] == week_number and x.date.year == year, self.innerHolidays)
        return filtered_holidays

    def displayHolidaysInWeek(self, holidayList):
        # Use your filter_holidays_by_week to get list of holidays within a week as a parameter
        # Output formated holidays in the week. 
        # * Remember to use the holiday __str__ method.
        for hol in holidayList:
            print(str(hol))

    def getWeather(self, year, weekNum):
        # Convert weekNum to range between two days
        # Use Try / Except to catch problems
        # Query API for weather in that week range
        # Format weather information and return weather string.
        url = "https://community-open-weather-map.p.rapidapi.com/forecast/daily"
        querystring = {"q":"minneapolis,us","cnt":"7","units":"imperial"}
        headers = {
                "X-RapidAPI-Host": "community-open-weather-map.p.rapidapi.com",
                "X-RapidAPI-Key": "48d10fe0acmsha06e72b55f0e490p193a53jsn27d1ee41a53f"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        weather = response.json()
        for value in weather['list']:
            date = datetime.fromtimestamp(value['dt'])
            print(str(date.date()) + ' - ' + value['weather'][0]['description'])

    def viewCurrentWeek(self):
        # Use the Datetime Module to look up current week and year
        # Use your filter_holidays_by_week function to get the list of holidays 
        # for the current week/year
        # Use your displayHolidaysInWeek function to display the holidays in the week
        # Ask user if they want to get the weather
        # If yes, use your getWeather function and display results
        today = date.today()
        week_num = today.isocalendar()[1]
        year = today.year
        filtered_holidays = self.filter_holidays_by_week(year, week_num)
        self.displayHolidaysInWeek(filtered_holidays)
        choice = input("Would you like to view the weather for this week?: ")
        if choice == 'y':
            self.getWeather(year, week_num)

    def removeDuplicates(self):
        # Removes duplicate holidays from the list.
        # An object is considered a duplicate of both date and name are equal
        print("Removing duplicates")
        for i,v in enumerate(self.innerHolidays):
            for j,w in enumerate(self.innerHolidays):
                if i != j:
                    if v.name == w.name and v.date == w.date:
                        self.innerHolidays.remove(w)
        print("Complete")


def printHolidayMenu():
    print('Holiday Menu')
    print('================')
    print('1. Add a Holiday')
    print('2. Remove a Holiday')
    print('3. Save Holiday List')
    print('4. View Holidays')
    print('5. Exit')

def main():
    # Large Pseudo Code steps
    # -------------------------------------
    # 1. Initialize HolidayList Object
    # 2. Load JSON file via HolidayList read_json function
    # 3. Scrape additional holidays using your HolidayList scrapeHolidays function.
    # 3. Create while loop for user to keep adding or working with the Calender
    # 4. Display User Menu (Print the menu)
    # 5. Take user input for their action based on Menu and check the user input for errors
    # 6. Run appropriate method from the HolidayList object depending on what the user input is
    # 7. Ask the User if they would like to Continue, if not, end the while loop, ending the program.  If they do wish to continue, keep the program going. 

    # create initial list object
    holiday_list = HolidayList([]) 

    # seed initial list and remove duplicate holidays
    holiday_list.read_json('holidays.json')
    holiday_list.scrapeHolidays()
    holiday_list.removeDuplicates()

    print("Holiday Managment")
    print("=================")
    print('There are ' + str(holiday_list.numHolidays()) + ' holidays stored in the system.')

    changes_saved = True

    while True:

        printHolidayMenu()

        option_num = input('Please choose an option: ')
        if option_num == '1':
            
            print("Add a Holiday")
            print("=============")

            name = input('Holiday: ')
            while True:
                date = input('Date: ')
                try:
                    datetime_obj = datetime.strptime(date, '%Y-%m-%d').date()
                except ValueError:
                    print("Error")
                    print('Invalid date. Please try again')
                else:
                    print('Success') 
                    holiday_list.addHoliday(Holiday(name, datetime_obj)) 
                    changes_saved = False
                    break

        elif option_num == '2':

            print('Remove a Holiday')
            print('================')

            while True:
                name = input('Holiday Name: ')
                date = input('Date: ')
                try:
                    datetime_obj = datetime.strptime(date, '%Y-%m-%d').date()
                except ValueError:
                    print('Error:')
                    print('Invalid date. Please try again')

                else:
                    if holiday_list.findHoliday(name, datetime_obj):
                        holiday_list.removeHoliday(name, datetime_obj)
                        print('Success:')
                        print(f'{name} has been removed from the holiday list')
                        changes_saved = False
                    else:
                        print('Error:')
                        print(f'{name} not found.')
                    break 

        elif option_num == '3': # SAVE LIST

            print('Saving Holiday List')
            print('====================')

            choice = input('Are you sure you want to save your changes? [y/n]: ')
            if choice == 'y':
                holiday_list.save_to_json('new_holidays.json')
                print('Success:')
                print('Your changes have been saved.')
                changes_saved = True
            elif choice == 'n':
                print('Canceled:')
                print('Holiday list file save canceled.')

        elif option_num == '4': # VIEW HOLIDAYS
            
            print('View Holidays')
            print('=================')

            year = int(input('Which year?: '))
            week_num = input('Which week? #[1-52, Leave blank for the current week]: ')

            if week_num == '':
                holiday_list.viewCurrentWeek()
            else:
                filtered_list = holiday_list.filter_holidays_by_week(year, int(week_num))
                holiday_list.displayHolidaysInWeek(filtered_list)

        elif option_num == '5': # EXIT

            print('Exit')
            print('=====')

            if changes_saved:
                choice = input('Are you sure you want to exit? [y/n] ')
                if choice == 'y':
                    print('Goodbye')
                    break
                elif choice == 'n':
                    continue
            else:
                print('Are you sure you want to exit?')
                print('Your changes will be lost.')
                choice = input('[y/n] ')
                if choice == 'y':
                    print('Goodbye')
                    break
                elif choice == 'n':
                    continue


if __name__ == "__main__":
    main();


# Additional Hints:
# ---------------------------------------------
# You may need additional helper functions both in and out of the classes, add functions as you need to.
#
# No one function should be more then 50 lines of code, if you need more then 50 lines of code
# excluding comments, break the function into multiple functions.
#
# You can store your raw menu text, and other blocks of texts as raw text files 
# and use placeholder values with the format option.
# Example:
# In the file test.txt is "My name is {fname}, I'm {age}"
# Then you later can read the file into a string "filetxt"
# and substitute the placeholders 
# for example: filetxt.format(fname = "John", age = 36)
# This will make your code far more readable, by seperating text from code.





