from django.test import RequestFactory, TestCase
from wagtail.models import Page
from staff.models import PersonPage, StaffIndexPage


class StaffIndexPageTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        root_page = Page.objects.get(pk=1)
        self.staff_index = StaffIndexPage(title="Колектив", slug="staff-test")
        root_page.add_child(instance=self.staff_index)

        # Create persons with different departments
        p1 = PersonPage(
            title="Олена Вєднікова",
            position="Директор",
            department="Керівництво ліцею",
        )
        p2 = PersonPage(
            title="Оксана Столяр",
            position="Вчитель",
            department="Кафедра природничих наук",
        )
        p3 = PersonPage(
            title="Олена Зарванська",
            position="Вчитель",
            department="Кафедра філології",
        )
        self.staff_index.add_child(instance=p2)
        self.staff_index.add_child(instance=p3)
        self.staff_index.add_child(instance=p1)

    def test_department_sorting_leadership_first(self):
        request = self.factory.get("/staff-test/")
        context = self.staff_index.get_context(request)
        departments = context["departments"]

        self.assertEqual(departments[0], "Керівництво ліцею")
        self.assertEqual(
            departments,
            ["Керівництво ліцею", "Кафедра природничих наук", "Кафедра філології"],
        )

