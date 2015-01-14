from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from test.testmodeltestcase import TestModelTestCase as Super
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import ConfigParser
from functools import partial
from itertools import chain
import unittest, re, time, os
from imuser import TemporaryUser


class Helper:
    def __init__(self, section, file):
        self.readline = partial(next, chain(("[{0}]\n".format(section),), file, ("",)))

class ListsOrder(Super):

    def setUp(self):
        Super.setUp(self)
        self.user = TemporaryUser("zombie-testing-account-login@intermine.org");
        self.user.create()

    def test_lists_order(self):

        config = ConfigParser.RawConfigParser(allow_no_value=True)
        with open("../../testmodel.properties") as ifh:
            config.readfp(Helper("Foo", ifh))
        su_name = config.get("Foo", "superuser.account")
        su_password = config.get("Foo", "superuser.initialPassword")

        # Log in as the SU
        browser = self.browser
        wait = WebDriverWait(browser, 10)

        browser.get(self.base_url + "/login.do")
        browser.find_element_by_name("username").clear()
        browser.find_element_by_name("username").send_keys(su_name)
        browser.find_element_by_name("password").clear()
        browser.find_element_by_name("password").send_keys(su_password)
        browser.find_element_by_name("action").click()

        # Go to the administrative user page
        browser.get(self.base_url + "/mymine.do?subtab=users")

        # Make the user an admin
        xpath = "//input[@value='zombie-testing-account-login@intermine.org']"
        checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        checkbox.click() if checkbox.is_selected() == False else True

        # Save the form
        xpath = "//input[@value='Save']"
        checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()

        # Log in as the new super user
        browser.get(self.base_url + "/logout.do")
        browser.get(self.base_url + "/login.do")

        wait.until(EC.visibility_of_element_located((By.NAME, "username")))
        browser.find_element_by_name("username").clear()
        browser.find_element_by_name("username").send_keys(self.user.name)
        browser.find_element_by_name("password").clear()
        browser.find_element_by_name("password").send_keys(self.user.password)
        browser.find_element_by_name("action").click()

        self.create_list_with_tags("OrderListFirst", "im:order:1")
        self.create_list_with_tags("OrderListFourth", "im:order:4")
        self.create_list_with_tags("OrderListThird", "im:order:3")
        self.create_list_with_tags("OrderListSecond", "im:order:2")

        # Visit our list page and make sure the orders are correct.
        # Use xpath's preceding-sibling to count the order.
        browser.get(self.base_url + "/bag.do?subtab=view")

        xpath_list1 = "//div[@id='all_bag_bag_item_line_OrderListFirst']/preceding-sibling::*"
        xpath_list2 = "//div[@id='all_bag_bag_item_line_OrderListSecond']/preceding-sibling::*"
        xpath_list3 = "//div[@id='all_bag_bag_item_line_OrderListThird']/preceding-sibling::*"
        xpath_list4 = "//div[@id='all_bag_bag_item_line_OrderListFourth']/preceding-sibling::*"

        # Wait for our lists to be present
        self.wait_for_elem("#all_bag_bag_item_line_OrderListFirst")

        sib_list1 = len(browser.find_elements_by_xpath(xpath_list1))
        sib_list2 = len(browser.find_elements_by_xpath(xpath_list2))
        sib_list3 = len(browser.find_elements_by_xpath(xpath_list3))
        sib_list4 = len(browser.find_elements_by_xpath(xpath_list4))

        self.assertTrue(sib_list4 > sib_list3 > sib_list2 > sib_list1, "Lists are not in the correct order.")

    def create_list_with_tags(self, name, tag):
        browser = self.browser
        wait = WebDriverWait(browser, 10)

        browser.get(self.base_url + "/bag.do?subtab=upload")
        self.wait_for_elem("#typeSelector")
        Select(self.browser.find_element_by_id("typeSelector")).select_by_visible_text("Employee")
        self.browser.find_element_by_id("pasteInput").send_keys("EmployeeA1, EmployeeA2, EmployeeA3")
        self.browser.find_element_by_id("submitBag").click()
        custom_list_name = name
        bagname = self.wait_for_elem("#newBagName")
        # bagname = self.browser.find_element_by_id("newBagName")
        bagname.clear()
        bagname.send_keys(custom_list_name)
        button = self.wait_for_elem("iframe")
        self.browser.switch_to_frame(self.browser.find_element_by_tag_name("iframe"))
        save_button = self.browser.find_element_by_class_name("save").click()
        add_tag_xpath = "//a[@class='addTagLink']"
        wait.until(EC.element_to_be_clickable((By.XPATH, add_tag_xpath))).click()
        new_tag_xpath = "//div[@id='listTags']//a[contains(@id, 'switchLink-inline-tag-editor')]"
        wait.until(EC.visibility_of_element_located((By.XPATH, new_tag_xpath))).click()
        new_tag_input_xpath = "//div[@id='listTags']//input[contains(@id, 'tagValue-inline-tag-editor')]"
        tag_input = wait.until(EC.visibility_of_element_located((By.XPATH, new_tag_input_xpath))).send_keys(tag)
        add_button_xpath = "//div[@id='listTags']//input[@value='Add']"
        wait.until(EC.visibility_of_element_located((By.XPATH, add_button_xpath))).click()
        done_buttom_xpath = "//div[@id='listTags']//input[@value='Done']"
        wait.until(EC.visibility_of_element_located((By.XPATH, done_buttom_xpath))).click()

    def tearDown(self):
        self.user.delete()
