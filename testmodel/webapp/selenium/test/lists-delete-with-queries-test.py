from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from test.testmodeltestcase import TestModelTestCase as Super
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from nose.plugins.skip import SkipTest
import unittest, re, time, os
from imuser import TemporaryUser

class ListsDeleteWithQueries(Super):

    def setUp(self):
        raise SkipTest
        Super.setUp(self)
        self.user = TemporaryUser("zombie-testing-account-login@intermine.org");
        self.user.create()

    def test_deleting_list_also_deletes_queries(self):
        # Log in as the SU
        browser = self.browser
        wait = WebDriverWait(browser, 10)

        # Log the user in.
        browser.get(self.base_url + "/login.do")
        wait.until(EC.visibility_of_element_located((By.NAME, "username")))
        browser.find_element_by_name("username").clear()
        browser.find_element_by_name("username").send_keys(self.user.name)
        browser.find_element_by_name("password").clear()
        browser.find_element_by_name("password").send_keys(self.user.password)
        browser.find_element_by_name("action").click()

        # Create a list
        list_name = "Custom List of Employees"
        self.create_list(list_name, "EmployeeA1, EmployeeA2, EmployeeA3")

        # Use this list in a query
        browser.get(self.base_url + "/customQuery.do")

        # Select Employee and continue
        classes = self.wait_for_elem("#queryClassSelector")
        Select(classes).select_by_visible_text("Employee")
        browser.find_element_by_id("submitClassSelect").click()

        # Select the summary
        button_summary_xpath = "//a[@title='Show Employee in results']"
        wait.until(EC.visibility_of_element_located((By.XPATH, button_summary_xpath))).click()

        # Add a constraint
        button_constraint_xpath = "//a[@title='Add a constraint to Employee']"
        wait.until(EC.visibility_of_element_located((By.XPATH, button_constraint_xpath))).click()

        # Select our list in the constraints
        self.wait_for_elem("#checkBoxBag").click()
        select_bag = self.wait_for_elem("#bag2")
        Select(select_bag).select_by_visible_text(list_name)
        browser.find_element_by_id("attributeSubmit").click()

        # Give the query a name
        query_name = "My Custom Query"
        query_name_xpath = "//form[@id='saveQueryForm']//input[@name='queryName']"
        wait.until(EC.visibility_of_element_located((By.XPATH, query_name_xpath))).send_keys(query_name)

        save_query_xpath = "//form[@id='saveQueryForm']//input[@value='Save query']"
        browser.find_element_by_xpath(save_query_xpath).click()

        time.sleep(30)

    def create_list(self, name, content):
        browser = self.browser
        wait = WebDriverWait(browser, 10)

        browser.get(self.base_url + "/bag.do?subtab=upload")
        self.wait_for_elem("#typeSelector")
        Select(self.browser.find_element_by_id("typeSelector")).select_by_visible_text("Employee")
        self.browser.find_element_by_id("pasteInput").send_keys(content)
        self.browser.find_element_by_id("submitBag").click()
        custom_list_name = name
        bagname = self.wait_for_elem("#newBagName")
        bagname.clear()
        bagname.send_keys(custom_list_name)
        button = self.wait_for_elem("iframe")
        self.browser.switch_to_frame(self.browser.find_element_by_tag_name("iframe"))
        save_button = self.browser.find_element_by_class_name("save").click()

    def tearDown(self):
        self.user.delete()
