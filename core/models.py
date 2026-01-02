from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings  # ✅ Correct import

class CustomUser(AbstractUser):
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=(('Male', 'Male'), ('Female', 'Female')))
    valid_until = models.DateField(null=True, blank=True)  # for subscription expiry

    def __str__(self):
        return self.username


class Progress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ FIXED LINE
    weight = models.FloatField()
    photo = models.ImageField(upload_to='progress_photos/')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}"
