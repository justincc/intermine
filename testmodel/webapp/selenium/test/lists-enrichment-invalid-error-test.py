import unittest

import selenium.webdriver.support.ui as ui
from test.testmodeltestcase import TestModelTestCase as Super
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ListEnrichmentInvalidCorrectionTest(Super):

    def setUp(self):
        Super.setUp(self)
        self.browser.get(self.base_url + '/bag.do?subtab=upload')

    def test_invalid_list_widget_correction(self):
        Select(self.browser.find_element_by_id("typeSelector")).select_by_visible_text("Employee")
        self.browser.find_element_by_id("pasteInput").send_keys("EmployeeA1, EmployeeA2, EmployeeA3")
        self.browser.find_element_by_id("submitBag").click()


        button = self.wait_for_elem("iframe")
        self.browser.switch_to_frame(self.browser.find_element_by_tag_name("iframe"))

        # Now find our buton in the iframe
        savebutton = self.browser.find_element_by_class_name("save").click()

        # Wait for one of our widgets:
        widget = self.wait_for_elem("#colleague_enrichment-widget")

        # Add one bogus value:
        self.browser.execute_script('var x=document.getElementsByName("errorCorrection");var i;for(i=0;i<x.length;i++){var option=document.createElement("option");option.text="Professor Farnsworth Correction";option.value="Professor Farnsworth Correction";x[i].add(option)}')

        # Get the Test Correction dropdown:
        dropdown = widget.find_element_by_name("errorCorrection")
        Select(dropdown).select_by_value("Professor Farnsworth Correction")

        element = WebDriverWait(self.browser, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-info"))
        )