from datetime import date
from django.test import RequestFactory, TestCase
from wagtail.models import Page, Site
from news.models import NewsIndexPage, NewsPage


class NewsSortingAndFilteringTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        root_page = Page.objects.get(pk=1)

        self.news_index = NewsIndexPage(
            title="Новини",
            slug="news-test",
            intro="<p>Новини ліцею</p>",
        )
        root_page.add_child(instance=self.news_index)
        self.news_index.save_revision().publish()

        default_site = Site.objects.filter(is_default_site=True).first()
        if default_site:
            default_site.root_page = root_page
            default_site.save()
        else:
            Site.objects.create(
                hostname="localhost",
                port=80,
                site_name="Test Site",
                root_page=root_page,
                is_default_site=True,
            )

        # Create news articles with different publication dates
        self.news_old = NewsPage(
            title="Стара новина",
            slug="stara-novyna",
            date=date(2025, 1, 10),
            intro="Опис старої новини",
        )
        self.news_index.add_child(instance=self.news_old)
        self.news_old.tags.add("Події")
        self.news_old.save_revision().publish()

        self.news_mid = NewsPage(
            title="Середня новина",
            slug="serednya-novyna",
            date=date(2025, 6, 15),
            intro="Опис середньої новини",
        )
        self.news_index.add_child(instance=self.news_mid)
        self.news_mid.tags.add("Олімпіади")
        self.news_mid.save_revision().publish()

        self.news_new = NewsPage(
            title="Нова новина",
            slug="nova-novyna",
            date=date(2025, 12, 20),
            intro="Опис нової новини",
        )
        self.news_index.add_child(instance=self.news_new)
        self.news_new.tags.add("Події")
        self.news_new.save_revision().publish()

    def test_default_sort_newer_to_older(self):
        request = self.factory.get("/news-test/")
        context = self.news_index.get_context(request)
        news_items = list(context["news_items"])

        self.assertEqual(context["current_order"], "desc")
        self.assertEqual(len(news_items), 3)
        self.assertEqual(news_items[0].title, "Нова новина")
        self.assertEqual(news_items[1].title, "Середня новина")
        self.assertEqual(news_items[2].title, "Стара новина")

    def test_explicit_desc_sort(self):
        request = self.factory.get("/news-test/?order=desc")
        context = self.news_index.get_context(request)
        news_items = list(context["news_items"])

        self.assertEqual(context["current_order"], "desc")
        self.assertEqual(news_items[0].title, "Нова новина")
        self.assertEqual(news_items[2].title, "Стара новина")

    def test_asc_sort_older_to_newer(self):
        request = self.factory.get("/news-test/?order=asc")
        context = self.news_index.get_context(request)
        news_items = list(context["news_items"])

        self.assertEqual(context["current_order"], "asc")
        self.assertEqual(len(news_items), 3)
        self.assertEqual(news_items[0].title, "Стара новина")
        self.assertEqual(news_items[1].title, "Середня новина")
        self.assertEqual(news_items[2].title, "Нова новина")

    def test_tag_filtering_with_default_desc_sort(self):
        request = self.factory.get("/news-test/?tag=Події")
        context = self.news_index.get_context(request)
        news_items = list(context["news_items"])

        self.assertEqual(context["current_tag"], "Події")
        self.assertEqual(context["current_order"], "desc")
        self.assertEqual(len(news_items), 2)
        self.assertEqual(news_items[0].title, "Нова новина")
        self.assertEqual(news_items[1].title, "Стара новина")

    def test_tag_filtering_with_asc_sort(self):
        request = self.factory.get("/news-test/?tag=Події&order=asc")
        context = self.news_index.get_context(request)
        news_items = list(context["news_items"])

        self.assertEqual(context["current_tag"], "Події")
        self.assertEqual(context["current_order"], "asc")
        self.assertEqual(len(news_items), 2)
        self.assertEqual(news_items[0].title, "Стара новина")
        self.assertEqual(news_items[1].title, "Нова новина")

    def test_render_page_contains_sort_controls(self):
        response = self.client.get(self.news_index.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Спочатку нові")
        self.assertContains(response, "Спочатку старі")
        self.assertContains(response, "Сортування:")

        response_asc = self.client.get(f"{self.news_index.url}?order=asc")
        self.assertEqual(response_asc.status_code, 200)
        self.assertContains(response_asc, "order=asc")
