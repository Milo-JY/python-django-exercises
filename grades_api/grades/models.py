from django.db import models

class Grade(models.Model):
    student_name = models.CharField(max_length=100)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name}: {self.score}"
