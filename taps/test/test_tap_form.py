""" Test cases:

- Tap form:
  - auth
    - unauth
    - as super
    - as normal
  - venue
    - not found
    - access denied
    - invalid mfg
    - valid mfg
  - tap:
    - new tap
    - invalid tap
    - existing tap

- Save tap form:
  - auth
    - (same)
  - venue
    - not found
    - access denied
    - valid
  - tap
    - new tap
    - existing tap
    - invalid tap
  - form
    - valid
    - invalid
      - gas type
      - venue
      - beer
      - est pct remaining
"""

from django.test import TestCase
from django.urls import reverse

from hsv_dot_beer.users.test.factories import UserFactory
from beers.models import Manufacturer
from beers.test.factories import ManufacturerFactory
from venues.test.factories import VenueFactory
from venues.models import VenueTapManager
from taps.test.factories import TapFactory


class ManufacturerSelectFormTest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.venue = VenueFactory()
        cls.normal_user = UserFactory()
        cls.manufacturers = Manufacturer.objects.bulk_create(
            ManufacturerFactory.build_batch(50)
        )
        cls.existing_tap = TapFactory(venue=cls.venue, beer=None)

    def setUp(self):
        self.create_url = reverse("create_tap_pick_mfg", args=[self.venue.id])
        self.edit_url = reverse(
            "edit_tap_pick_mfg", args=[self.venue.id, self.existing_tap.tap_number]
        )

    def test_unauthenticated_create(self):
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            reverse("login") + "?next=" + self.create_url,
        )

    def test_unauthenticated_edit(self):
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            reverse("login") + "?next=" + self.edit_url,
        )

    def test_unowned(self):
        self.client.force_login(self.normal_user)
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 404)
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 404)

    def test_venue_not_found(self):
        self.client.force_login(UserFactory(is_superuser=True))
        response = self.client.get(
            reverse("create_tap_pick_mfg", args=[self.venue.id - 1])
        )
        self.assertEqual(response.status_code, 404)

    def test_tap_not_found(self):
        self.client.force_login(UserFactory(is_superuser=True))
        response = self.client.get(
            reverse(
                "edit_tap_pick_mfg",
                args=[self.venue.id, self.existing_tap.tap_number - 1],
            )
        )
        # This doesn't cause a 404 yet. We should probably fix that eventually
        self.assertEqual(response.status_code, 200)

    def test_superuser(self):
        self.client.force_login(UserFactory(is_superuser=True))
        # session, user, venue, managers, count mfgs, mfg list
        with self.assertNumQueries(6):
            response = self.client.get(self.create_url)
        self.assertTemplateUsed("beers/manufacturer-select.html")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode("utf-8")
        for manufacturer in self.manufacturers:
            self.assertIn(manufacturer.name, body)
        self.assertIn(reverse("create_tap", args=[self.venue.id]), body)
        self.assertNotIn("selected", body)

    def test_superuser_edit(self):
        self.client.force_login(UserFactory(is_superuser=True))
        # session, user, venue, managers, count manufacturers, manufacturers
        with self.assertNumQueries(6):
            response = self.client.get(self.edit_url)
        self.assertTemplateUsed("beers/manufacturer-select.html")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode("utf-8")
        for manufacturer in self.manufacturers:
            self.assertIn(manufacturer.name, body)
        self.assertIn(
            reverse("edit_tap", args=[self.venue.id, self.existing_tap.tap_number]),
            body,
        )

    def test_normal_user_create_with_default(self):
        default_mfg = self.manufacturers[10]
        VenueTapManager.objects.create(
            venue=self.venue,
            user=self.normal_user,
            default_manufacturer=default_mfg,
        )
        self.client.force_login(self.normal_user)
        # session, user, venue, managers, count mfgs, mfg list
        with self.assertNumQueries(6):
            response = self.client.get(self.create_url)
        self.assertTemplateUsed("beers/manufacturer-select.html")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode("utf-8")
        for manufacturer in self.manufacturers:
            self.assertIn(manufacturer.name, body)
        self.assertIn(reverse("create_tap", args=[self.venue.id]), body)
        self.assertIn(f'<option value="{default_mfg.id}"  selected>', body)

    def test_normal_user_edit_with_default(self):
        default_mfg = self.manufacturers[10]
        VenueTapManager.objects.create(
            venue=self.venue,
            user=self.normal_user,
            default_manufacturer=default_mfg,
        )
        self.client.force_login(self.normal_user)
        # session, user, venue, managers, count mfgs, mfg list
        with self.assertNumQueries(6):
            response = self.client.get(self.edit_url)
        self.assertTemplateUsed("beers/manufacturer-select.html")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode("utf-8")
        for manufacturer in self.manufacturers:
            self.assertIn(manufacturer.name, body)
        self.assertIn(
            reverse("edit_tap", args=[self.venue.id, self.existing_tap.tap_number]),
            body,
        )
        # NOTE the two spaces are intentional
        self.assertIn(f'<option value="{default_mfg.id}"  selected>', body)

    def test_normal_user_create_with_no_default(self):
        VenueTapManager.objects.create(
            venue=self.venue,
            user=self.normal_user,
        )
        self.client.force_login(self.normal_user)
        # session, user, venue, managers, count mfgs, mfg list
        with self.assertNumQueries(6):
            response = self.client.get(self.create_url)
        self.assertTemplateUsed("beers/manufacturer-select.html")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode("utf-8")
        for manufacturer in self.manufacturers:
            self.assertIn(manufacturer.name, body)
        self.assertIn(reverse("create_tap", args=[self.venue.id]), body)
        self.assertNotIn("selected", body)

    def test_normal_user_edit_with_no_default(self):
        VenueTapManager.objects.create(
            venue=self.venue,
            user=self.normal_user,
        )
        self.client.force_login(self.normal_user)
        # session, user, venue, managers, count mfgs, mfg list
        with self.assertNumQueries(6):
            response = self.client.get(self.edit_url)
        self.assertTemplateUsed("beers/manufacturer-select.html")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode("utf-8")
        for manufacturer in self.manufacturers:
            self.assertIn(manufacturer.name, body)
        self.assertIn(
            reverse("edit_tap", args=[self.venue.id, self.existing_tap.tap_number]),
            body,
        )
        self.assertNotIn("selected", body)
