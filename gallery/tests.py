from datetime import date
from django.test import RequestFactory, TestCase
from wagtail.images.models import Image
from wagtail.models import Page
from gallery.models import GalleryAlbumPage, GalleryImage, GalleryIndexPage


class GallerySortingTest(TestCase):
    def setUp(self):
        root = Page.get_first_root_node()
        self.home = Page.objects.filter(depth=2).first()
        if not self.home:
            self.home = Page(title="Home", slug="home")
            root.add_child(instance=self.home)

        self.gallery_index = GalleryIndexPage(title="Галерея", slug="gallery")
        self.home.add_child(instance=self.gallery_index)

        # Create dummy images
        self.img1 = Image.objects.create(title="Photo 1", file="photos/test1.jpg", width=800, height=600)
        self.img2 = Image.objects.create(title="Photo 2", file="photos/test2.jpg", width=800, height=600)
        self.img3 = Image.objects.create(title="Photo 3", file="photos/test3.jpg", width=800, height=600)

        # Create albums with different dates
        self.album_old = GalleryAlbumPage(
            title="Old Event",
            slug="old-event",
            date=date(2023, 5, 10),
        )
        self.gallery_index.add_child(instance=self.album_old)
        GalleryImage.objects.create(page=self.album_old, image=self.img1, sort_order=0)

        self.album_new = GalleryAlbumPage(
            title="New Event",
            slug="new-event",
            date=date(2026, 8, 20),
        )
        self.gallery_index.add_child(instance=self.album_new)
        GalleryImage.objects.create(page=self.album_new, image=self.img2, sort_order=0)

        self.album_mid = GalleryAlbumPage(
            title="Mid Event",
            slug="mid-event",
            date=date(2025, 1, 15),
        )
        self.gallery_index.add_child(instance=self.album_mid)
        GalleryImage.objects.create(page=self.album_mid, image=self.img3, sort_order=0)

        self.factory = RequestFactory()

    def test_albums_sorted_by_date_descending_by_default(self):
        request = self.factory.get("/gallery/")
        context = self.gallery_index.get_context(request)
        albums = context["albums"]
        self.assertEqual(len(albums), 3)
        self.assertEqual(albums[0].title, "New Event")
        self.assertEqual(albums[1].title, "Mid Event")
        self.assertEqual(albums[2].title, "Old Event")

    def test_albums_sorted_by_date_ascending_with_order_param(self):
        request = self.factory.get("/gallery/?order=asc")
        context = self.gallery_index.get_context(request)
        albums = context["albums"]
        self.assertEqual(len(albums), 3)
        self.assertEqual(albums[0].title, "Old Event")
        self.assertEqual(albums[1].title, "Mid Event")
        self.assertEqual(albums[2].title, "New Event")

    def test_photos_view_sorted_by_date(self):
        request = self.factory.get("/gallery/?view=photos")
        context = self.gallery_index.get_context(request)
        all_photos = context["all_photos"]
        self.assertEqual(len(all_photos), 3)
        self.assertEqual(all_photos[0]["album"].title, "New Event")
        self.assertEqual(all_photos[1]["album"].title, "Mid Event")
        self.assertEqual(all_photos[2]["album"].title, "Old Event")
