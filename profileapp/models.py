from django.db import models
from backend_functions.universal_values import *
import os
from digischool.settings import BASE_DIR, MEDIA_ROOT

class USER_PROFILE_DATABASE(models.Model):
	edit_once = models.BooleanField(default=False)
	user_signup_db_mapping = models.OneToOneField("loginapp.USER_SIGNUP_DATABASE", on_delete=models.CASCADE)
	user_profile_photo = models.FileField(upload_to="image/", null=True, verbose_name="", default=f"{MEDIA_ROOT}/image/profile_photo.jpg")
	father_name = models.CharField(max_length=NAME_LIMIT, default="")
	mother_name = models.CharField(max_length=NAME_LIMIT, default="")