from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import User, Field

class FieldTests(APITestCase):

    def setUp(self):
        # Creating a test user
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass', role='farmer', email='testuser@gmail.com')
        self.another_user = User.objects.create_user(username='anotheruser', password='testpass2', role='farmer', email='anotheruser@gmail.com')
        self.field_data = {
            'name': 'Test Field',
            'location': 'POINT(5 5)',  # example location
            'description': 'This is a test field.'
        }

    def test_add_field(self):
        self.client.force_authenticate(user=self.user)
        self.client.login(username='testuser', password='testpass')
        
        url = reverse('add_field')
        response = self.client.post(url, self.field_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Field.objects.count(), 1)
        self.assertEqual(Field.objects.get().name, 'Test Field')
        self.client.logout()

    
    def test_list_fields(self):
        # Add a field first
        self.test_add_field()
        self.client.force_authenticate(user=self.user)
        self.client.login(username='testuser', password='testpass')
        
        url = reverse('my_fields')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.client.logout()


    def test_unauthorized_field_creation(self):
        url = reverse('add_field')
        response = self.client.post(url, self.field_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Field.objects.count(), 0)
        self.client.logout()


    def test_field_modification_by_owner(self):
        self.test_add_field()  # First, add a field
        
        field = Field.objects.get()
        url = reverse('update_field', args=[field.id])
        updated_data = {
            'name': 'Updated Field Name',
            'location': 'POINT(6 6)',
            'description': 'Updated description.'
        }
        self.client.force_authenticate(user=self.user)
        self.client.login(username='testuser', password='testpass')
        response = self.client.put(url, updated_data, format='json')
        
        field.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(field.name, 'Updated Field Name')
        self.client.logout()


    def test_field_modification_by_non_owner(self):
        self.test_add_field()  # First, add a field

        field = Field.objects.get()
        url = reverse('update_field', args=[field.id])
        self.client.force_authenticate(user=self.another_user)
        self.client.login(username='anotheruser', password='testpass2')
        response = self.client.put(url, self.field_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()


    def test_field_deletion_by_owner(self):
        self.test_add_field()  # First, add a field
        field = Field.objects.get()
        url = reverse('delete_field', args=[field.id])
        self.client.force_authenticate(user=self.user)
        self.client.login(username='testuser', password='testpass')
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Field.objects.count(), 0)
        self.client.logout()


    def test_field_deletion_by_non_owner(self):
        self.test_add_field()  # First, add a field

        field = Field.objects.get()
        url = reverse('delete_field', args=[field.id])
        self.client.force_authenticate(user=self.another_user)
        self.client.login(username='anotheruser', password='testpass2')
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Field.objects.count(), 1)
        self.client.logout()

