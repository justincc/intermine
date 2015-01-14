import unittest

import selenium.webdriver.support.ui as ui
from test.testmodeltestcase import TestModelTestCase as Super
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class ListsFilterByName(Super):

    def setUp(self):
        Super.setUp(self)
        self.browser.get(self.base_url + '/bag.do?subtab=view')

    def test_lists_filter_by_name(self):

        wait = WebDriverWait(self.browser, 10)
        filterText = self.browser.find_element_by_id("filterText")

        # Filter out "Places-I-Have-Worked"
        filterText.clear()
        filterText.send_keys("employee")
        time.sleep(3) 
        element = wait.until(EC.invisibility_of_element_located((By.ID,'all_bag_bag_item_line_Places-I-Have-Worked')))
        element = wait.until(EC.visibility_of_element_located((By.ID,'all_bag_bag_chck_Everyones-Favourite-Employees')))

        # Filter out "Everyones-Favourite-Employees"
        filterText.clear()
        filterText.send_keys("worked")
        time.sleep(3)
        element = wait.until(EC.invisibility_of_element_located((By.ID,'all_bag_bag_chck_Everyones-Favourite-Employees')))
        element = wait.until(EC.visibility_of_element_located((By.ID,'all_bag_bag_item_line_Places-I-Have-Worked')))

        # Filter out everything
        filterText.clear()
        filterText.send_keys("nothing-should-ever-match-this")
        time.sleep(3)
        element = wait.until(EC.invisibility_of_element_located((By.ID,'all_bag_bag_chck_Everyones-Favourite-Employees')))
        element = wait.until(EC.invisibility_of_element_located((By.ID,'all_bag_bag_item_line_Places-I-Have-Worked')))
        
        # Clear filter
        savebutton = self.browser.find_element_by_id("reset_button").click()
        time.sleep(3)
        element = wait.until(EC.visibility_of_element_located((By.ID,'all_bag_bag_chck_Everyones-Favourite-Employees')))
        element = wait.until(EC.visibility_of_element_located((By.ID,'all_bag_bag_item_line_Places-I-Have-Worked')))