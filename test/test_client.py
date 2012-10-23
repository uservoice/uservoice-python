import yaml
import unittest
import uservoice

class TestClient(unittest.TestCase):
    def setUp(self):
        super(TestClient, self).setUp()
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

    def test_should_not_create_KB_article_as_regular_user(self):
        nobody = self.client.login_as('regular_user@example.com')

        def func():
            result = nobody.post("/api/v1/articles.json", {
                'article': { 'title': 'good morning' }
            })

        self.assertRaises(uservoice.Unauthorized, func)

    def test_should_not_get_current_user_as_nobody(self):
        def func():
            result = self.client.get("/api/v1/users/current")

        self.assertRaises(uservoice.Unauthorized, func)

    def test_should_get_access_token_as_owner(self):
        with self.client.login_as_owner() as owner:
          self.assertTrue(owner.get("/api/v1/users/current.json")['user']['roles']['owner'])
          with owner.login_as('regular@example.com') as regular:
              self.assertTrue(owner.get("/api/v1/users/current.json")['user']['roles']['owner'])
              self.user = regular.get("/api/v1/users/current.json")['user']
              self.assertFalse(self.user['roles']['owner'])
        self.assertEqual(self.user['email'], 'regular@example.com')


    def test_should_generate_not_found_on_unexistant_endpoint(self):
        def func():
            result = self.client.get("/api/v1/lanterns/1")

        self.assertRaises(uservoice.NotFound, func)

    def test_should_not_get_unexistant_user(self):
        def func():
            self.client.get("/api/v1/users/86723562378523")

        self.assertRaises(uservoice.NotFound, func)

    def test_should_get_reasonable_collection_using_collection_class(self):
        suggestions = self.client.get_collection("/api/v1/suggestions")
        count = 0
        for suggestion in suggestions:
            count += 1
        self.assertEqual(count, len(suggestions))

    def test_should_get_reasonable_collection_using_collection_class(self):
        suggestions = self.client.get_collection("/api/v1/suggestions", limit=1)
        count = 0
        for suggestion in suggestions:
            count += 1
        self.assertEqual(len(suggestions), 1)

    def test_should_get_page_of_tickets(self):
        tickets = self.client.get("/api/v1/tickets?per_page=2")
        self.assertEqual(len(tickets), 2)
