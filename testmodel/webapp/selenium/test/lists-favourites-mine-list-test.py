from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from test.testmodeltestcase import TestModelTestCase as Super
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


import unittest, re
from imuser import TemporaryUser

class ListFavourites(Super):

    def setUp(self):
        Super.setUp(self)
        self.user = TemporaryUser("zombie-testing-account-login@intermine.org");
        self.user.create()

    def test_lists_favourites_and_my_filter(self):

        browser = self.browser
        browser.get(self.base_url + "/login.do")
        browser.find_element_by_name("username").clear()
        browser.find_element_by_name("username").send_keys(self.user.name)
        browser.find_element_by_name("password").clear()
        browser.find_element_by_name("password").send_keys(self.user.password)
        browser.find_element_by_name("action").click()

        # Create a list
        browser.get(self.base_url + "/bag.do?subtab=upload")
        self.wait_for_elem("#typeSelector")
        Select(self.browser.find_element_by_id("typeSelector")).select_by_visible_text("Employee")
        self.browser.find_element_by_id("pasteInput").send_keys("EmployeeA1, EmployeeA2, EmployeeA3")
        self.browser.find_element_by_id("submitBag").click()

        # Set the name to something we know
        custom_list_name = "CustomList1"
        # bagname = self.browser.find_element_by_id("newBagName")
        bagname = self.wait_for_elem("#newBagName")
        bagname.clear()
        bagname.send_keys(custom_list_name)

        # The bag upload save button lives inside an iframe
        button = self.wait_for_elem("iframe")
        self.browser.switch_to_frame(self.browser.find_element_by_tag_name("iframe"))
        save_button = self.browser.find_element_by_class_name("save").click()

        # View available lists.
        browser.get(self.base_url + "/bag.do?subtab=view")

        # Confirm that we have two templates that are not mine and one that is mine
        self.assert_visible_id('all_bag_bag_chck_Everyones-Favourite-Employees')
        self.assert_visible_id('all_bag_bag_item_line_Places-I-Have-Worked')
        self.assert_visible_id('all_bag_bag_item_line_' + custom_list_name)

        # Click the "my" button to only the user specific lists
        my_button = self.browser.find_element_by_id("filter_scope_all_bag_bag").click()
        self.assert_invisible_id('all_bag_bag_item_line_Places-I-Have-Worked')
        self.assert_invisible_id('all_bag_bag_chck_Everyones-Favourite-Employees')
        self.assert_visible_id('all_bag_bag_item_line_' + custom_list_name)

        # Reset the filters.
        reset_button = self.browser.find_element_by_id("reset_button").click()

        # Confirm that all lsits are showing.
        self.assert_visible_id('all_bag_bag_item_line_Places-I-Have-Worked')
        self.assert_visible_id('all_bag_bag_item_line_' + custom_list_name)
        self.assert_visible_id('all_bag_bag_chck_Everyones-Favourite-Employees')

        # Make one of the lists our favourite:
        list_favourite_button = self.browser.find_element_by_id("favourite_Places-I-Have-Worked").click()

        # Filter to show only our favourites:
        favourite_button = self.browser.find_element_by_id("filter_favourites_all_bag_bag").click()
        self.assert_invisible_id('all_bag_bag_item_line_' + custom_list_name)
        self.assert_invisible_id('all_bag_bag_chck_Everyones-Favourite-Employees')
        self.assert_visible_id('all_bag_bag_item_line_Places-I-Have-Worked')

        # Reset the filters.
        reset_button = self.browser.find_element_by_id("reset_button").click()
        self.assert_visible_id('all_bag_bag_item_line_' + custom_list_name)
        self.assert_visible_id('all_bag_bag_chck_Everyones-Favourite-Employees')
        self.assert_visible_id('all_bag_bag_item_line_Places-I-Have-Worked')

    def assert_visible_id(self, id):
        elem = self.wait().until(lambda d: d.find_element_by_id(id))
        self.wait().until(lambda d: elem.is_displayed())
        self.assertTrue(elem.is_displayed())

    def assert_invisible_id(self, id):
        elem = self.wait().until(lambda d: d.find_element_by_id(id))
        self.wait().until_not(lambda d: elem.is_displayed())
        self.assertFalse(elem.is_displayed())

    def tearDown(self):
        self.user.delete()
