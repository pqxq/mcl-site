from datetime import datetime, time

from django.core.paginator import Paginator
from django.db import models
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

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
            .select_related("owner")
            .prefetch_related("tags", "gallery_images__image")
            .only(
                "title",
                "slug",
                "first_published_at",
                "search_description",
                "live",
                "owner",
                "date",
                "intro",
                "cover_image",
            )
        )

    def _get_photo_date(self, album):
        if album.date:
            return timezone.make_aware(
                datetime.combine(album.date, time.min),
                timezone.get_current_timezone(),
            )
        return album.first_published_at or timezone.now()

    def _build_photo_list(self, albums, order="desc"):
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
                        "sort_order": getattr(image, "sort_order", 0),
                    }
                )
        reverse_sort = (order != "asc")
        all_photos.sort(
            key=lambda item: (
                item["date"],
                -item["sort_order"] if reverse_sort else item["sort_order"],
            ),
            reverse=reverse_sort,
        )
        return all_photos

    class Meta:
        verbose_name = "Галерея (системна)"

    @method_decorator(cache_page(60 * 15))
    def serve(self, request, *args, **kwargs):
        return super().serve(request, *args, **kwargs)

    def __str__(self) -> str:
        return self.title

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Get view mode: 'albums' (default) or 'photos'
        view_mode = request.GET.get("view", "albums")
        if view_mode not in {"albums", "photos"}:
            view_mode = "albums"
        context["view_mode"] = view_mode

        all_albums = self._base_album_queryset()

        # Sorting by date (default: newest first)
        order = request.GET.get("order", "desc").strip().lower()
        if order in ["asc", "oldest", "older"]:
            current_order = "asc"
            ordered_albums = all_albums.order_by(
                models.F("date").asc(nulls_last=True), "first_published_at"
            )
        else:
            current_order = "desc"
            ordered_albums = all_albums.order_by(
                models.F("date").desc(nulls_last=True), "-first_published_at"
            )

        context["current_order"] = current_order

        # Filter by tag if requested
        tag_filter = request.GET.get("tag", "").strip()
        albums = ordered_albums
        if tag_filter:
            albums = albums.filter(tags__name=tag_filter).distinct()

        albums = list(albums)
        context["albums"] = albums

        # Get photos for 'photos' view mode via direct queryset pagination (24 per page)
        # Prevents loading hundreds or thousands of photo objects into Python RAM
        if view_mode == "photos":
            album_ids = [a.id for a in albums]
            photos_qs = (
                GalleryImage.objects.filter(page_id__in=album_ids)
                .select_related("image", "page")
            )
            if current_order == "asc":
                photos_qs = photos_qs.order_by(
                    models.F("page__date").asc(nulls_last=True),
                    "page__first_published_at",
                    "sort_order",
                )
            else:
                photos_qs = photos_qs.order_by(
                    models.F("page__date").desc(nulls_last=True),
                    "-page__first_published_at",
                    "-sort_order",
                )
            paginator = Paginator(photos_qs, 24)
            page_number = request.GET.get("page", 1)
            photos_page = paginator.get_page(page_number)
            context["all_photos"] = photos_page
            context["photos_page"] = photos_page

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

    def __str__(self) -> str:
        return str(self.tag)


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
        ordering = ["-date", "-first_published_at"]

    def __str__(self) -> str:
        return self.title


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

    @property
    def album(self):
        """Backward-compatible alias for template rendering"""
        return self.page

    def __getitem__(self, key):
        """Enable dictionary subscript access like item['album'] for backward compatibility"""
        if key == "album":
            return self.page
        if key == "image":
            return self.image
        if key == "caption":
            return self.caption
        if key == "sort_order":
            return getattr(self, "sort_order", 0)
        if key == "date":
            if self.page.date:
                return timezone.make_aware(
                    datetime.combine(self.page.date, time.min),
                    timezone.get_current_timezone(),
                )
            return self.page.first_published_at or timezone.now()
        raise KeyError(key)

    def __str__(self) -> str:
        return self.caption or self.image.title
