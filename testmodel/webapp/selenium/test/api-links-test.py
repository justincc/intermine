import unittest
import selenium.webdriver.support.ui as ui
from test.testmodeltestcase import TestModelTestCase as Super

class APILinksTest(Super):

    def setUp(self):
        Super.setUp(self)
        self.browser.get(self.base_url)

    def test_api_links(self):
        # Look for Perl content
        self.browser.get(self.base_url + '/api.do?subtab=perl')
        header = self.wait_for_elem('#apiPerl')
        self.assertIn("Perl Web Service Client", header.text)

        # Look for Python content
        self.browser.get(self.base_url + '/api.do?subtab=python')
        header = self.wait_for_elem('#apipython')
        self.assertIn("Python Web Service Client", header.text)

        # Look for Ruby content
        self.browser.get(self.base_url + '/api.do?subtab=ruby')
        header = self.wait_for_elem('#apiruby')
        self.assertIn("Ruby Web Service Client", header.text)

        # Look for Java content
        self.browser.get(self.base_url + '/api.do?subtab=java')
        header = self.wait_for_elem('#apiJava')
        self.assertIn("Java Web Service Client", header.text)