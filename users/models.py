from django.contrib.auth.models import AbstractUser
from django_mongodb_backend.fields import ObjectIdAutoField

class CustomUser(AbstractUser):
    id = ObjectIdAutoField(primary_key=True)

    def __str__(self):
        return self.username
