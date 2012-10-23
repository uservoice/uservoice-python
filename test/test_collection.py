import yaml
import unittest
import uservoice

ELEMENTS = 1501
class TestCollection(unittest.TestCase):
    def setUp(self):
        super(TestCollection, self).setUp()
        with open('test/config.yml') as f:
            self.config = yaml.load(f)
        class MockClient:
            def __init__(self, result):
                self.result = result
            def get(self, path):
                return self.result
        self.clientWithEmptySet = MockClient({"response_data": {"page": 1, "per_page": uservoice.PER_PAGE, "total_records": 0, "filter": "all", "sort": "votes"}, "suggestions": []})
        self.clientWithOne = MockClient({"response_data": {"page": 1, "per_page":  uservoice.PER_PAGE, "total_records": 1, "filter": "all", "sort": "votes"},
            "suggestions": [{
                "url": "http://uservoice-subdomain.uservoice.com/forums/1-general/suggestions/1-idea",
                "id": 1,
                "state": "published",
                "title": "a",
                "text": "b",
                "formatted_text": "b",
                "forum": {"id": "1", "name": "General"}
            }]})
        class PagedClient:
            def get(self, path):
                page = int(path[len(path) - 1])
                page_first_index = uservoice.PER_PAGE * (page - 1) + 1
                page_last_index = min(uservoice.PER_PAGE * page, ELEMENTS)
                if "/api/v1/suggestions?per_page=" in path:
                    suggestions = []
                    for idea_index in range(page_first_index, page_last_index+1):
                        suggestions.append({
                          "url": "http://uservoice-subdomain.uservoice.com/forums/1-general/suggestions/" + str(idea_index) + "-idea",
                          "id": idea_index,
                          "state": "published",
                          "title": "Idea",
                          "text": "Idea",
                          "formatted_text": "Idea",
                          "forum": {"id": "1", "name": "General"}
                        })
                    return {
                      "response_data": {
                        "page": page,
                        "per_page": uservoice.PER_PAGE,
                        "total_records": ELEMENTS,
                        "filter": "all",
                        "sort": "votes"
                      },
                      "suggestions": suggestions
                    }
                else:
                    raise ValueError(path + 'not supported in PagedClient')
        self.pagedClient = PagedClient()

    def test_getting_zero_size(self):
        collection = uservoice.Collection(self.clientWithEmptySet, '/api/v1/suggestions')
        self.assertEqual(len(collection), 0)

    def test_enumerating_zero_elements(self):
        collection = uservoice.Collection(self.clientWithEmptySet, '/api/v1/suggestions')
        for i in collection:
            raise IndexError

    def test_getting_one_element(self):
        collection = uservoice.Collection(self.clientWithOne, '/api/v1/suggestions')
        self.assertEqual(collection[0]['id'], 1)

    def test_yielding_once(self):
        collection = uservoice.Collection(self.clientWithOne, '/api/v1/suggestions')
        count = 0
        for i in collection:
            count += 1
        self.assertEqual(count, 1)

    def test_len_of_1(self):
        collection = uservoice.Collection(self.clientWithOne, '/api/v1/suggestions')
        self.assertEqual(len(collection), 1)

    def test_correct_size_with_paged_client(self):
        collection = uservoice.Collection(self.pagedClient, '/api/v1/suggestions')
        self.assertEqual(len(collection), ELEMENTS)

    def test_yield_correct_number_of_times_with_paged_client(self):
        collection = uservoice.Collection(self.pagedClient, '/api/v1/suggestions')
        count = 0
        for i in collection:
            count += 1
        self.assertEqual(count, ELEMENTS)

    def test_yield_correct_number_of_times_with_paged_client_and_limit(self):
        collection = uservoice.Collection(self.pagedClient, '/api/v1/suggestions', limit=1001)
        count = 0
        for i in collection:
            count += 1
        self.assertEqual(count, 1001)

    def test_limited_size_with_paged_client_and_limit(self):
        collection = uservoice.Collection(self.pagedClient, '/api/v1/suggestions', limit=1001)
        self.assertEqual(len(collection), 1001)

    def test_limited_size_with_paged_client_and_limit(self):
        collection = uservoice.Collection(self.pagedClient, '/api/v1/suggestions', limit=1001)
        def func():
            collection[1001]
        self.assertRaises(IndexError, func)

    def test_accessing_out_of_bounds_element_in_first_page_with_really_small_limited_size_with_paged_client(self):
        collection = uservoice.Collection(self.pagedClient, '/api/v1/suggestions', limit=2)
        def func():
            collection[2]
        self.assertRaises(IndexError, func)

    def test_accessing_element_in_first_page_with_really_small_limited_size_with_paged_client(self):
        collection = uservoice.Collection(self.pagedClient, '/api/v1/suggestions', limit=2)
        self.assertEqual(collection[1]['id'], 2)

