from django.db import models
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.search import index
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

class GalleryIndexPage(Page):
    """Index page for the photo gallery"""
    
    page_description = "Розділ галереї (створюється один раз)"
    
    intro = RichTextField("Вступний текст", blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    parent_page_types = ['home.HomePage']
    subpage_types = ['gallery.GalleryAlbumPage']
    max_count = 1
    
    # Fixed slug for the gallery page
    slug = 'gallery'
    
    def full_clean(self, *args, **kwargs):
        # Force the slug to always be 'gallery'
        self.slug = 'gallery'
        super().full_clean(*args, **kwargs)
    
    class Meta:
        verbose_name = "Галерея (системна)"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        
        # Get view mode: 'albums' (default) or 'photos'
        view_mode = request.GET.get('view', 'albums')
        context['view_mode'] = view_mode
        
        # Get published albums, ordered by date descending
        albums = self.get_children().live().specific().order_by('-first_published_at')
        
        # Filter by tag if requested
        tag_filter = request.GET.get('tag', '')
        if tag_filter:
            albums = [album for album in albums if tag_filter in [tag.name for tag in album.tags.all()]]
        
        context['albums'] = albums
        
        # Get all photos for 'photos' view mode
        if view_mode == 'photos':
            from datetime import datetime
            all_photos = []
            for album in self.get_children().live().specific():
                for img in album.gallery_images.all():
                    # Convert date to datetime for consistent comparison
                    photo_date = album.date
                    if photo_date and not isinstance(photo_date, datetime):
                        photo_date = datetime.combine(photo_date, datetime.min.time())
                    if not photo_date:
                        photo_date = album.first_published_at
                    
                    all_photos.append({
                        'image': img.image,
                        'caption': img.caption,
                        'album': album,
                        'date': photo_date
                    })
            # Sort by date descending
            all_photos.sort(key=lambda x: x['date'], reverse=True)
            context['all_photos'] = all_photos
        
        # Get all tags for filtering logic
        from taggit.models import Tag
        album_ids = [p.id for p in self.get_children().live()]
        tags = Tag.objects.filter(galleryalbumpage__id__in=album_ids).distinct()
        context['tags'] = tags
        context['current_tag'] = tag_filter
        
        return context


class GalleryAlbumTag(TaggedItemBase):
    content_object = ParentalKey(
        'GalleryAlbumPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


class GalleryAlbumPage(Page):
    """Specific event or album"""
    date = models.DateField("Дата події", null=True, blank=True)
    intro = models.CharField("Короткий опис", max_length=250, blank=True)
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Обкладинка альбому"
    )
    
    tags = ClusterTaggableManager(through=GalleryAlbumTag, blank=True, verbose_name="Теги")

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('tags'),
        FieldPanel('cover_image'),
        InlinePanel('gallery_images', label="Фотографії"),
    ]

    parent_page_types = ['gallery.GalleryIndexPage']
    subpage_types = []

    class Meta:
        verbose_name = "Альбом"
        verbose_name_plural = "Альбоми"


class GalleryImage(Orderable):
    page = ParentalKey(GalleryAlbumPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name="Фото"
    )
    caption = models.CharField("Підпис", max_length=250, blank=True)

    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]
