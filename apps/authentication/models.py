

from django.contrib.auth.models import AbstractUser, Group

from django.db import models

class User(AbstractUser):
    role_choices = [
        ('admin', 'admin'),
        ('warehouse', 'warehouse'),
        ('sales','sales'),
    ]

    role =  models.CharField(max_length=20,choices=role_choices,default='sales')
    phone = models.CharField(max_length=20)
    avatar = models.ImageField(upload_to='assets/img/avatars/',blank=True,null=True)

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"

    @property
    def full_name(self):
        """Lấy tên đầy đủ"""
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username