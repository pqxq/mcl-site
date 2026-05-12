from datetime import datetime, time

from django.db import models
from django.utils import timezone

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import Tag, TaggedItemBase
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index

class GalleryIndexPage(Page):
    """Index page for the photo gallery"""

    page_description = "Розділ галереї (створюється один раз)"

    intro = RichTextField("Вступний текст", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["gallery.GalleryAlbumPage"]
    max_count = 1

    # Fixed slug for the gallery page
    slug = "gallery"

    def full_clean(self, *args, **kwargs):
        # Force the slug to always be 'gallery'
        self.slug = "gallery"
        super().full_clean(*args, **kwargs)

    def _base_album_queryset(self):
        return (
            GalleryAlbumPage.objects.child_of(self)
            .live()
            .public()
            .prefetch_related("tags", "gallery_images__image")
            .order_by("-date", "-first_published_at")
        )

    def _get_photo_date(self, album):
        if album.date:
            return timezone.make_aware(
                datetime.combine(album.date, time.min),
                timezone.get_current_timezone(),
            )
        return album.first_published_at

    def _build_photo_list(self, albums):
        all_photos = []
        for album in albums:
            photo_date = self._get_photo_date(album)
            for image in album.gallery_images.all():
                all_photos.append(
                    {
                        "image": image.image,
                        "caption": image.caption,
                        "album": album,
                        "date": photo_date,
                    }
                )
        all_photos.sort(key=lambda item: item["date"], reverse=True)
        return all_photos

    class Meta:
        verbose_name = "Галерея (системна)"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Get view mode: 'albums' (default) or 'photos'
        view_mode = request.GET.get("view", "albums")
        if view_mode not in {"albums", "photos"}:
            view_mode = "albums"
        context["view_mode"] = view_mode

        all_albums = self._base_album_queryset()

        # Filter by tag if requested
        tag_filter = request.GET.get("tag", "").strip()
        albums = all_albums
        if tag_filter:
            albums = albums.filter(tags__name=tag_filter).distinct()

        albums = list(albums)
        context["albums"] = albums

        # Get all photos for 'photos' view mode
        if view_mode == "photos":
            context["all_photos"] = self._build_photo_list(albums)

        # Get all tags for filtering logic
        context["tags"] = (
            Tag.objects.filter(
                galleryalbumpage__id__in=all_albums.values_list("id", flat=True)
            )
            .distinct()
            .order_by("name")
        )
        context["current_tag"] = tag_filter

        return context


class GalleryAlbumTag(TaggedItemBase):
    content_object = ParentalKey(
        "GalleryAlbumPage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


class GalleryAlbumPage(Page):
    """Specific event or album"""
    date = models.DateField("Дата події", null=True, blank=True)
    intro = models.CharField("Короткий опис", max_length=250, blank=True)
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Обкладинка альбому",
    )

    tags = ClusterTaggableManager(through=GalleryAlbumTag, blank=True, verbose_name="Теги")

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("intro"),
        FieldPanel("tags"),
        FieldPanel("cover_image"),
        InlinePanel("gallery_images", label="Фотографії"),
    ]

    parent_page_types = ["gallery.GalleryIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Альбом"
        verbose_name_plural = "Альбоми"


class GalleryImage(Orderable):
    page = ParentalKey(GalleryAlbumPage, on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name="Фото",
    )
    caption = models.CharField("Підпис", max_length=250, blank=True)

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]
