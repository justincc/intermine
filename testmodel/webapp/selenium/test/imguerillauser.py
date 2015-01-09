import requests
import json
import os
import uuid
import random
import time
import string
from nose.plugins.skip import Skip, SkipTest

DEFAULT_BASE = 'http://localhost:8080/intermine-demo'

class IMGuerillaUser:
    """A helper class for creating new users on a target webservice"""

    def __init__(self, password=None):
        self.base_url = os.getenv('TESTMODEL_BASE', DEFAULT_BASE)
        self.password = password if password is not None else 'password'

    def create(self):
        """Create the new user - SHOULD BE CALLED IN SETUP"""

        try:
            self.delete()
        except:
            pass

        self.name = "intermine-test"
        epoch_time = str(int(time.time()))
        rhash = ''.join(random.choice(string.digits) for _ in range(8))
        self.name += epoch_time
        self.name += rhash

        url = "http://api.guerrillamail.com/ajax.php?f=set_email_user&email_user=" + self.name
        guerilla_result = requests.get(url)
        
        json = guerilla_result.json()

        self.guerilla = json

        self.name = self.guerilla["email_addr"]

        methodURI = '/service/users'
        payload = {'name': self.name, 'password': self.password}

        result = requests.post(self.base_url + methodURI, data=payload)
        j = result.json()


        if j['statusCode'] == 200:
            print "User created successfully: " + self.name
        else:
            print "Error creating user: " + j['error']

    def _get_deregistration_token(self):
        """Get the deregistration token for this user"""
        methodURI = '/service/user/deregistration'
        result = requests.post(self.base_url + methodURI, auth=(self.name, self.password))

        j = result.json()
        return j['token']['uuid']

    def delete(self):
        print "deleting with password", self.password
        """Delete this user from the webservice - YOU MUST CALL THIS IN tearDown!!"""
        methodURI = '/service/user'
        payload = {'deregistrationToken': self._get_deregistration_token()}
        requests.delete(self.base_url + methodURI, params=payload, auth=(self.name, self.password))

        url = "http://api.guerrillamail.com/ajax.php?f=forget_me&sid_token=" + self.guerilla["sid_token"]
        return requests.get(url).json()

    def list_mail(self):
        url = "http://api.guerrillamail.com/ajax.php?f=get_email_list&offset=0&sid_token=" + self.guerilla["sid_token"]
        return requests.get(url).json()

    def get_last_mail(self):
        response = self.list_mail()
        mail_id = response["list"][0]["mail_id"]
        url = "http://api.guerrillamail.com/ajax.php?f=fetch_email&email_id=" + str(mail_id) + "&sid_token=" + str(self.guerilla["sid_token"])
        return requests.get(url).json()

    def set_password(self, password):
        self.password = password