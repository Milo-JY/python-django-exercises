from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import Grade
from .serializers import GradeSerializer
from django.contrib.auth.models import User

# 단위 테스트: 모델
class GradeModelTest(TestCase):
    def setUp(self):
        self.grade = Grade.objects.create(student_name='Alice', score=85)

    def test_grade_str(self):
        self.assertEqual(str(self.grade), 'Alice: 85')

    def test_grade_fields(self):
        self.assertEqual(self.grade.student_name, 'Alice')
        self.assertEqual(self.grade.score, 85)
        self.assertIsNotNone(self.grade.created_at)

# API 테스트: 엔드포인트
class GradeAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.token = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'testpass'
        }).data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.url = reverse('grades:grade-list')
        self.stats_url = reverse('grades:grade-stats')
        self.valid_payload = {'student_name': 'Bob', 'score': 90}
        self.invalid_payload = {'student_name': '', 'score': -10}
        self.grade = Grade.objects.create(student_name='Charlie', score=88)

    def test_get_grade_list_unauthenticated(self):
        self.client.credentials()  # 토큰 제거
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_grade_list(self):
        response = self.client.get(self.url)
        grades = Grade.objects.all()
        serializer = GradeSerializer(grades, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_valid_grade(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Grade.objects.count(), 2)
        self.assertEqual(response.data['student_name'], 'Bob')
        self.assertEqual(response.data['score'], 90)

    def test_create_invalid_grade(self):
        response = self.client.post(self.url, self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_grade_detail(self):
        response = self.client.get(f"{self.url}{self.grade.id}/")
        serializer = GradeSerializer(self.grade)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_grade(self):
        update_payload = {'student_name': 'Charlie Updated', 'score': 92}
        response = self.client.put(f"{self.url}{self.grade.id}/", update_payload, format='json')
        self.grade.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.grade.student_name, 'Charlie Updated')
        self.assertEqual(self.grade.score, 92)

    def test_delete_grade(self):
        response = self.client.delete(f"{self.url}{self.grade.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Grade.objects.count(), 0)

    def test_get_grade_stats(self):
        Grade.objects.create(student_name='Bob', score=90)
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('mean', response.data)
        self.assertIn('median', response.data)
        self.assertIn('mode', response.data)
        self.assertEqual(response.data['mean'], 89.0)
        self.assertEqual(response.data['median'], 89.0)
        self.assertEqual(response.data['mode'], 88)

    def test_get_grade_stats_empty(self):
        Grade.objects.all().delete()
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'No grades available')