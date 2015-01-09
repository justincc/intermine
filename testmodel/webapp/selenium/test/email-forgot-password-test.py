from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from test.testmodeltestcase import TestModelTestCase as Super
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from imguerillauser import IMGuerillaUser
import xml.etree.ElementTree as ET
import unittest, re, time

class EmailForgotPasswordTest(Super):

    def setUp(self):
        Super.setUp(self)
        self.im_guerilla_user = IMGuerillaUser("password");
        self.im_guerilla_user.create()

    def test_email_forgot_link(self):
        # Create a second web driver for the sharee account
        browser = self.browser

        # Confirm that we can log in
        browser.get(self.base_url + "/login.do")
        browser.find_element_by_name("username").clear()
        browser.find_element_by_name("username").send_keys(self.im_guerilla_user.name)
        browser.find_element_by_name("password").clear()
        browser.find_element_by_name("password").send_keys(self.im_guerilla_user.password)
        browser.find_element_by_name("action").click()
        welcome_message = self.wait_for_elem("#msg")
        self.assertIn('Logged in as user "' + self.im_guerilla_user.name + '"', welcome_message.text)

        # Log out and then request password reset email
        browser.get(self.base_url + "/logout.do")
        browser.get(self.base_url + "/login.do")

        # Make sure that the password request form is hidden
        wait = WebDriverWait(browser, 10)

        self.wait_for_elem("#passwordDiv")
        password_reset_div = wait.until(EC.invisibility_of_element_located((By.ID,'passwordDiv')))

        # Toggle the password reset form
        forgot_password_link = browser.find_element_by_xpath('//div[@id="login"]//a').click()

        # Make sure that the password request form is shown
        password_reset_div = wait.until(EC.visibility_of_element_located((By.ID,'passwordDiv')))

        # Enter our email address into the password reset form
        username_input = browser.find_element_by_xpath('//form[@id="requestPasswordForm"]//input[@name="username"]')
        username_input.send_keys(self.im_guerilla_user.name)
        request_password_button = browser.find_element_by_xpath('//form[@id="requestPasswordForm"]//input[@name="action"]').click()

        time.sleep(20)

        # Get out user's latest email.
        last_mail = self.im_guerilla_user.get_last_mail()

        print "last_mail", last_mail
        mail_body = last_mail["mail_body"].decode('string_escape')

        # Parse our password reset link
        root = ET.fromstring(mail_body)
        href = root.find(".//a").get("href")

        # Open our password reset link
        browser.get(self.base_url)
        browser.get(href)

        new_password = "newpassword"

        # Enter our new password
        browser.find_element_by_xpath('//input[@name="newpassword"]').send_keys(new_password)
        browser.find_element_by_xpath('//input[@name="newpassword2"]').send_keys(new_password)
        browser.find_element_by_xpath('//input[@value="Change password"]').click()

        # Confirm password was changed
        password_changed_message = self.wait_for_elem("#msg")
        self.assertIn("Your password was changed successfully", password_changed_message.text)
        self.im_guerilla_user.set_password(new_password)
        
        # Log out / Log in using new password
        browser.get(self.base_url + "/logout.do")
        browser.get(self.base_url + "/login.do")
        browser.find_element_by_name("username").clear()
        browser.find_element_by_name("username").send_keys(self.im_guerilla_user.name)
        browser.find_element_by_name("password").clear()
        browser.find_element_by_name("password").send_keys(self.im_guerilla_user.password)
        browser.find_element_by_name("action").click()
        welcome_message = self.wait_for_elem("#msg")
        self.assertIn('Logged in as user "' + self.im_guerilla_user.name + '"', welcome_message.text)
        
    def tearDown(self):
        self.im_guerilla_user.delete()