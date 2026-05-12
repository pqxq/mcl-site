from django.test import RequestFactory, SimpleTestCase

from .views import search


class SearchViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_empty_query_returns_empty_page(self):
        request = self.factory.get("/search/", {"query": "   ", "page": "2"})
        response = search(request)

        self.assertEqual(response.context_data["search_query"], "")
        self.assertEqual(response.context_data["search_results"].number, 1)
        self.assertEqual(len(response.context_data["search_results"].object_list), 0)
