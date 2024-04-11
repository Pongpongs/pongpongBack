from django.db import models

# Create your models here.
class UserProfile(models.Model):
	email = models.CharField(max_length=100)

	def __str__(self):
		return self.login
