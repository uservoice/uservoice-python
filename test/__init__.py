# -*- coding: utf-8 -*-
import sys
import os
import unittest
import yaml
import simplejson as json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import uservoice


class UserVoiceTestCase(unittest.TestCase):
    def setUp(self):
        super(UserVoiceTestCase, self).setUp()
        with open('test/config.yml') as f:
            self.config = yaml.load(f)
        self.client = uservoice.Client(self.config['subdomain_name'],
                                       self.config['api_key'],
                                       self.config['api_secret'])
    def test_2_legged_user_reqest(self):
        users = json.load(self.client.request('get', "/api/v1/users.json"))

        for user_hash in users['users']:
            print 'User: "' + user_hash['name'] + '", Profile URL: ' + user_hash['url']

    # TODO
    #def test_2_legged_user_reqest_with_sso(self):
    #    self.client.login_as('raimo@uservoice.com')
    #    users = json.load(self.client.request('get', "/api/v1/users/current.json"))

    #    with users['user'] as user:
    #        print 'User: "' + user['name'] + '", Profile URL: ' + user['url']

if __name__ == '__main__':
    unittest.main()