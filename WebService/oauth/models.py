from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Additional fields related to the user can be added here

class UserAccessToken(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='access_token')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_in = models.IntegerField(default=3600)  # Default expiry time in seconds, adjust as needed

    @property
    def is_expired(self):
        """Check if the token is expired."""
        return now() > self.created_at + self.expires_in
