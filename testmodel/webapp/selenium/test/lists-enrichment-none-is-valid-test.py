import unittest

import selenium.webdriver.support.ui as ui
from test.testmodeltestcase import TestModelTestCase as Super
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import time

class ListEnrichmentNoneIsValidTest(Super):

    def setUp(self):
        Super.setUp(self)
        self.browser.get(self.base_url + '/bag.do?subtab=upload')

    def test_none_is_valid_correction_strategy(self):
        Select(self.browser.find_element_by_id("typeSelector")).select_by_visible_text("Employee")
        self.browser.find_element_by_id("pasteInput").send_keys("EmployeeA1, EmployeeA2, EmployeeA3")
        self.browser.find_element_by_id("submitBag").click()

        button = self.wait_for_elem("iframe")
        self.browser.switch_to_frame(self.browser.find_element_by_tag_name("iframe"))

        # Now find our buton in the iframe
        savebutton = self.browser.find_element_by_class_name("save").click()

        # Wait for one of our widgets:
        widget = self.wait_for_elem("#colleague_enrichment-widget")

        # Get the Test Correction dropdown:
        dropdown = widget.find_element_by_name("errorCorrection")

        # Get all of the available options for the widget:
        options = dropdown.find_elements_by_tag_name("option")

        # SELENIUM QUIRKINESS:
        # Changing the value of a select element detaches the element from the DOM!
        # Therefore save the values to a list and iterate through that instead.

        # Save the list of values
        optionValues = []
        for option in options:
            optionValues.append(option.get_attribute("value"))

        # Loop through our values to validate each one.
        for value in optionValues:

            # Rediscover our dropdown
            dropdown = widget.find_element_by_name("errorCorrection")

            # Change the value
            myselect = Select(dropdown).select_by_value(value)

            # Give time for the DOM to update and an error to possibly appear
            time.sleep(5)

            # Make sure that we don't get an alert (which is an error)
            try:
                error = self.browser.find_element_by_class_name("alert-info")
                if error:
                    self.browser.quit()
            except:
                pass