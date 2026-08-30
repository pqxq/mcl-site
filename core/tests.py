from django.test import TestCase
from wagtail.rich_text import expand_db_html


class ExternalLinkHandlerTest(TestCase):
    def test_external_http_link_opens_in_new_tab(self):
        input_html = '<p>Check <a href="http://example.com">Example</a></p>'
        output_html = expand_db_html(input_html)
        self.assertIn('target="_blank"', output_html)
        self.assertIn('rel="noopener noreferrer"', output_html)
        self.assertIn('href="http://example.com"', output_html)

    def test_external_https_link_opens_in_new_tab(self):
        input_html = '<p>Visit <a href="https://example.org/test?a=1&b=2">Example</a></p>'
        output_html = expand_db_html(input_html)
        self.assertIn('target="_blank"', output_html)
        self.assertIn('rel="noopener noreferrer"', output_html)

    def test_mailto_link_does_not_open_in_new_tab(self):
        input_html = '<p>Email us at <a href="mailto:info@example.com">info@example.com</a></p>'
        output_html = expand_db_html(input_html)
        self.assertNotIn('target="_blank"', output_html)
        self.assertIn('href="mailto:info@example.com"', output_html)

    def test_anchor_link_does_not_open_in_new_tab(self):
        input_html = '<p>Jump to <a href="#heading">heading</a></p>'
        output_html = expand_db_html(input_html)
        self.assertNotIn('target="_blank"', output_html)
        self.assertIn('href="#heading"', output_html)


class SidebarActiveLinkTest(TestCase):
    def setUp(self):
        from core.models import SidebarSection, SidebarLink
        from wagtail.models import Page, Site

        root = Page.get_first_root_node()
        self.home = Page.objects.filter(depth=2).first()
        if not self.home:
            self.home = Page(title="Home", slug="home")
            root.add_child(instance=self.home)

        self.child_page = Page(title="Положення", slug="polozhennia")
        self.home.add_child(instance=self.child_page)

        # Create sidebar sections
        self.section1 = SidebarSection.objects.create(
            title="Головна",
            icon="bi-house",
            order=1,
            is_expanded=False
        )
        SidebarLink.objects.create(
            section=self.section1,
            label="Головна",
            page=self.home,
            sort_order=0
        )

        self.section2 = SidebarSection.objects.create(
            title="Публічна інформація",
            icon="bi-file-text",
            order=2,
            is_expanded=False
        )
        self.link1 = SidebarLink.objects.create(
            section=self.section2,
            label="Установчі документи",
            external_url="/publichna-informatsiia/ustanovchi/",
            sort_order=0
        )
        self.link2 = SidebarLink.objects.create(
            section=self.section2,
            label="Положення",
            page=self.child_page,
            sort_order=1
        )

    def test_active_sublink_expands_parent_section(self):
        from django.test import RequestFactory
        from core.templatetags.core_menu import get_sidebar_sections

        factory = RequestFactory()
        request = factory.get(self.child_page.url)

        context = {
            'request': request,
            'page': self.child_page,
        }

        sections = get_sidebar_sections(context)
        self.assertEqual(len(sections), 2)

        # Section 1 (Home) should not be active
        self.assertFalse(sections[0].has_active_link)
        self.assertFalse(sections[0].is_open)

        # Section 2 (Публічна інформація) should have active link and be open
        self.assertTrue(sections[1].has_active_link)
        self.assertTrue(sections[1].is_open)

        # Check that child link 2 (Положення) is active and link 1 is not
        valid_links = sections[1].valid_links
        self.assertFalse(valid_links[0].is_active)
        self.assertTrue(valid_links[1].is_active)
