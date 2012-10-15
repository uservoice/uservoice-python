# -*- coding: utf-8 -*-
import sys
import os
import unittest
import yaml
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
    def test_getting_first_10_users(self):
        users = self.client.get("/api/v1/users")['users']
        self.assertEqual(len(users), 10)

    def test_login_as_owner(self):
        owner_token = self.client.login_as_owner()
        user = owner_token.get("/api/v1/users/current")['user']
        self.assertTrue(user['roles']['owner'])

    def test_login_as_regular_user(self):
        token = self.client.login_as('someguy@example.com')
        user = token.get("/api/v1/users/current.json")['user']
        self.assertFalse(user['roles']['owner'])
        self.assertEqual(user['email'], 'someguy@example.com')

    def test_login_with_access_token(self):
        old_client = self.client.login_as('someguy@example.com')

        new_client = uservoice.Client(self.config['subdomain_name'],
                                          self.config['api_key'],
                                          self.config['api_secret'])
        reloaded_token = new_client.login_with_access_token(old_client.token, old_client.secret)

        user = reloaded_token.get("/api/v1/users/current.json")['user']
        self.assertFalse(user['roles']['owner'])
        self.assertEqual(user['email'], 'someguy@example.com')


if __name__ == '__main__':
    unittest.main()