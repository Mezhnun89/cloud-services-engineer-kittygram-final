from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import Cat


class CatAccessTests(APITestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user('owner', password='test-pass')
        self.other = get_user_model().objects.create_user('reader', password='test-pass')
        self.cat = Cat.objects.create(
            name='Kitty', color='white', birth_year=2020, owner=self.owner,
        )
        self.url = f'/api/cats/{self.cat.pk}/'

    def test_anonymous_cannot_list_cats(self):
        self.assertEqual(self.client.get('/api/cats/').status_code, 401)

    def test_other_user_can_read_but_cannot_edit_or_delete(self):
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(self.url).status_code, 200)
        self.assertEqual(self.client.patch(self.url, {'name': 'Changed'}).status_code, 403)
        self.assertEqual(self.client.delete(self.url).status_code, 403)
        self.cat.refresh_from_db()
        self.assertEqual(self.cat.name, 'Kitty')

    def test_owner_can_edit_and_delete(self):
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.patch(self.url, {'name': 'Snow'}).status_code, 200)
        self.cat.refresh_from_db()
        self.assertEqual(self.cat.name, 'Snow')
        self.assertEqual(self.client.delete(self.url).status_code, 204)

    def test_creation_sets_owner_and_converts_color(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post('/api/cats/', {
            'name': 'Snow', 'birth_year': 2024, 'color': '#ffffff',
            'owner': self.other.pk,
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['owner'], self.owner.pk)
        self.assertEqual(response.data['color'], 'white')

    def test_pagination_has_ten_cats_per_page(self):
        Cat.objects.bulk_create([
            Cat(name=f'Cat{i}', color='black', birth_year=2020, owner=self.owner)
            for i in range(10)
        ])
        self.client.force_authenticate(self.owner)
        response = self.client.get('/api/cats/')
        self.assertEqual(response.data['count'], 11)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIsNotNone(response.data['next'])
