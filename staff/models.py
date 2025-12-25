from django.db import models
from wagtail.models import Page, Orderable
from wagtail.search import index
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey

class StaffIndexPage(Page):
    
    page_description = "Розділ колективу (створюється один раз)"
    
    intro = RichTextField("Вступ", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    max_count = 1
    subpage_types = ['staff.PersonPage']
    parent_page_types = ['home.HomePage']
    
    class Meta:
        verbose_name = "Колектив (системна)"

    def get_context(self, request):
        context = super().get_context(request)
        # Get all departments for filtering
        from staff.models import PersonPage
        departments = PersonPage.objects.live().exclude(department='').values_list('department', flat=True).distinct()
        context['departments'] = sorted(set(departments))
        
        # Filter by department if requested
        dept_filter = request.GET.get('department', '')
        staff_members = list(self.get_children().live().specific())
        if dept_filter:
            staff_members = [p for p in staff_members if hasattr(p, 'department') and p.department == dept_filter]
        context['staff_members'] = staff_members
        context['current_department'] = dept_filter
        return context

class PersonPage(Page):
    position = models.CharField("Посада", max_length=100)
    department = models.CharField("Кафедра", max_length=200, blank=True, 
                                   help_text="Наприклад: Кафедра філології, Кафедра точних наук")
    education = models.CharField("Освіта", max_length=255, blank=True)
    category = models.CharField("Кваліфікаційна категорія", max_length=100, blank=True)
    experience = models.CharField("Стаж роботи", max_length=50, blank=True)
    bio = RichTextField("Біографія та досягнення", blank=True)
    photo = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name="Фото"
    )

    content_panels = Page.content_panels + [
        FieldPanel('photo'),
        FieldPanel('position'),
        FieldPanel('department'),
        InlinePanel('subjects', label="Предмети"),
        FieldPanel('education'),
        FieldPanel('category'),
        FieldPanel('experience'),
        FieldPanel('bio'),
    ]

    parent_page_types = ['staff.StaffIndexPage']
    subpage_types = []

    search_fields = Page.search_fields + [
        index.SearchField('title', boost=2),
        index.SearchField('position', boost=2),
        index.SearchField('department'),
        index.SearchField('education'),
        index.SearchField('category'),
        index.SearchField('experience'),
        index.SearchField('bio'),
    ]

class TeacherSubject(Orderable):
    page = ParentalKey(PersonPage, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField("Назва предмета", max_length=100)

    panels = [
        FieldPanel('name'),
    ]
