# Python Django Exercises
Django와 Django REST Framework를 사용한 REST API 연습 프로젝트.

## 프로젝트
- `grades_api`: 학생 성적 관리 API.
  - 앱: `grades` (모델, 시리얼라이저, 뷰셋).
  - 엔드포인트: `/grades/`, `/grades/grades/`.

## 설치
```bash
python3 -m venv django_venv
source django_venv/bin/activate
pip install -r requirements.txt
cd grades_api
python manage.py migrate
python manage.py runserver