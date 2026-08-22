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
