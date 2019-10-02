from django.test import TestCase


class TestBackend(TestCase):

    def test_get(self):

        response = self.client.get('/get-request/', {'q': 'hello'})
        # self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.status_code, 200)

    def test_post(self):

        response = self.client.post('/post-request/', {'q': 'hello'})
        self.assertEqual(response.status_code, 200)
