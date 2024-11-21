from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from classes.models import Class
from datetime import timedelta


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.trainer = User.objects.create_user(username="trainer",
                                                email="trainer@example.com",
                                                password="password")
        self.other_user = User.objects.create_user(username="otheruser",
                                                   email="otheruser@example.com",
                                                   password="password")
        self.client.force_authenticate(user=self.trainer)

        self.class_instance = Class.objects.create(
            name="Yoga Class",
            description="A relaxing yoga session.",
            date_time=timezone.now() + timedelta(days=1),
            duration=60,
            max_participants=10,
            trainer=self.trainer
        )


class ClassModelTest(BaseTestCase):
    def test_class_str_representation(self):
        self.assertEqual(str(self.class_instance), "Yoga Class")

    def test_class_creation(self):
        new_class = Class.objects.create(
            name="Pilates Class",
            description="Strength and flexibility training.",
            date_time=timezone.now() + timedelta(days=2),
            duration=75,
            max_participants=15,
            trainer=self.trainer
        )
        self.assertEqual(Class.objects.count(), 2)
        self.assertEqual(new_class.trainer, self.trainer)


from classes.serializers import ClassSerializer


class ClassSerializerTest(BaseTestCase):
    def test_serializer_data(self):
        serializer = ClassSerializer(instance=self.class_instance)
        expected_data = {
            'id': self.class_instance.id,
            'name': "Yoga Class",
            'description': "A relaxing yoga session.",
            'date_time': self.class_instance.date_time,
            'duration': 60,
            'max_participants': 10,
            'trainer': self.trainer.id,
        }
        self.assertDictContainsSubset(expected_data, serializer.data)

    def test_read_only_fields(self):
        data = {
            'name': "Pilates Class",
            'description': "A new pilates class.",
            'date_time': timezone.now() + timedelta(days=2),
            'duration': 45,
            'max_participants': 20,
            'trainer': self.trainer.id
        }
        serializer = ClassSerializer(data=data)
        serializer.is_valid()
        saved_instance = serializer.save(trainer=self.trainer)
        self.assertEqual(saved_instance.trainer, self.trainer)


class ClassViewTest(BaseTestCase):
    def test_list_classes(self):
        response = self.client.get("/classes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Yoga Class")

    def test_create_class(self):
        data = {
            "name": "Pilates Class",
            "description": "A new pilates class.",
            "date_time": timezone.now() + timedelta(days=2),
            "duration": 45,
            "max_participants": 20
        }
        response = self.client.post("/classes/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Class.objects.count(), 2)
        new_class = Class.objects.get(name="Pilates Class")
        self.assertEqual(new_class.trainer, self.trainer)

    def test_create_class_unauthenticated(self):
        self.client.logout()
        data = {
            "name": "Pilates Class",
            "description": "A new pilates class.",
            "date_time": timezone.now() + timedelta(days=2),
            "duration": 45,
            "max_participants": 20
        }
        response = self.client.post("/classes/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_class_detail(self):
        response = self.client.get(f"/classes/{self.class_instance.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Yoga Class")

    def test_update_class_by_trainer(self):
        data = {
            "name": "Updated Yoga Class",
            "description": "An updated relaxing yoga session.",
            "date_time": timezone.now() + timedelta(days=1),
            "duration": 90,
            "max_participants": 15
        }
        response = self.client.put(f"/classes/{self.class_instance.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.class_instance.refresh_from_db()
        self.assertEqual(self.class_instance.name, "Updated Yoga Class")
        self.assertEqual(self.class_instance.duration, 90)

    def test_update_class_not_trainer(self):
        self.client.force_authenticate(user=self.other_user)
        data = {
            "name": "Unauthorized Update",
            "description": "This should not succeed.",
        }
        response = self.client.put(f"/classes/{self.class_instance.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_class_by_trainer(self):
        response = self.client.delete(f"/classes/{self.class_instance.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Class.objects.count(), 0)

    def test_delete_class_not_trainer(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(f"/classes/{self.class_instance.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Class.objects.count(), 1)


