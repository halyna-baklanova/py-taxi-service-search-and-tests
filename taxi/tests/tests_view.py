from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model


from django.urls import reverse

from taxi.models import Driver, Car, Manufacturer

INDEX_URL = reverse("taxi:index")
DRIVER_LIST_URL = reverse("taxi:driver-list")
CAR_LIST_URL = reverse("taxi:car-list")
MANUFACTURER_LIST_URL = reverse("taxi:manufacturer-list")


class PublicRequiredTests(TestCase):
    def test_index(self) -> None:
        response = self.client.get(INDEX_URL)
        self.assertNotEqual(response.status_code, 200)

    def test_driver_list(self):
        response = self.client.get(DRIVER_LIST_URL)
        self.assertNotEqual(response.status_code, 200)

    def test_car_list(self):
        response = self.client.get(CAR_LIST_URL)
        self.assertNotEqual(response.status_code, 200)

    def test_manufacturer_list(self):
        response = self.client.get(MANUFACTURER_LIST_URL)
        self.assertNotEqual(response.status_code, 200)


class PrivateTestsWithoutFilter(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="driver",
            password="password",
        )
        self.client.force_login(self.user)

    def test_retrieve_driver_list(self) -> None:
        Driver.objects.create(username="user1", license_number="ABC12345")
        Driver.objects.create(username="user2", license_number="ABC54321")
        response = self.client.get(DRIVER_LIST_URL)
        drivers = Driver.objects.all()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["driver_list"]), list(drivers)
        )
        self.assertTemplateUsed(response, "taxi/driver_list.html")

    def test_retrieve_car_list(self) -> None:
        manufacturer = Manufacturer.objects.create(
            name="TestManufacturer", country="TestCountry"
        )

        Car.objects.create(model="Car1", manufacturer=manufacturer)
        Car.objects.create(model="Car2", manufacturer=manufacturer)

        response = self.client.get(CAR_LIST_URL)
        cars = Car.objects.all()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["car_list"]), list(cars))
        self.assertTemplateUsed(response, "taxi/car_list.html")

    def test_retrieve_manufacturer_list(self) -> None:
        Manufacturer.objects.create(name="Manufacturer1", country="Country1")
        Manufacturer.objects.create(name="Manufacturer2", country="Country2")
        response = self.client.get(MANUFACTURER_LIST_URL)
        manufacturers = Manufacturer.objects.all()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["manufacturer_list"]), list(manufacturers)
        )
        self.assertTemplateUsed(response, "taxi/manufacturer_list.html")


class PrivateTestsWithFilter(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="driver",
            password="password",
        )
        self.client.force_login(self.user)

        self.manufacturer = Manufacturer.objects.create(
            name="TestManufacturer", country="TestCountry"
        )

        Driver.objects.create(username="user1", license_number="ABC12345")
        Driver.objects.create(username="user2", license_number="ABC54321")

        Car.objects.create(model="Car1", manufacturer=self.manufacturer)
        Car.objects.create(model="Car2", manufacturer=self.manufacturer)

        Manufacturer.objects.create(name="Manufacturer1", country="Country1")
        Manufacturer.objects.create(name="Manufacturer2", country="Country2")

    def test_search_driver_by_username(self):
        response = self.client.get(DRIVER_LIST_URL, {"username": "user1"})
        drivers = Driver.objects.filter(username__icontains="user1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["driver_list"]), list(drivers))
        self.assertTemplateUsed(response, "taxi/driver_list.html")

    def test_search_car_by_model(self):
        response = self.client.get(CAR_LIST_URL, {"model": "Car1"})
        cars = Car.objects.filter(model__icontains="Car1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["car_list"]), list(cars))
        self.assertTemplateUsed(response, "taxi/car_list.html")

    def test_search_manufacturer_by_name(self):
        response = self.client.get(
            MANUFACTURER_LIST_URL, {"name": "Manufacturer1"}
        )
        manufacturers = Manufacturer.objects.filter(
            name__icontains="Manufacturer1"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["manufacturer_list"]), list(manufacturers)
        )
        self.assertTemplateUsed(response, "taxi/manufacturer_list.html")
