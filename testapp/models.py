from django.db import models
from backend_functions.universal_values import *

class ALL_TESTS(models.Model):
	test_title = models.CharField(max_length=TEST_TITLE_LENGTH)
	test_instruction = models.TextField()
	start_datetime = models.DateTimeField()
	end_datetime = models.DateTimeField()
	files = models.FileField(upload_to="test_files/", null=True, verbose_name="")  
	test_unique_id = models.CharField(max_length=TEST_UNIQUE_ID) # "course_id(10):test_series_number(2)"
	course_mapping = models.ForeignKey("courseapp.AVAILABLE_COURSES", on_delete=models.CASCADE)
	test_questions = models.TextField() # contains file path
	test_data = models.TextField() # # contains scores. json format {"maximumscore": 100, "minimumscore":0 , loginapp.USER_SIGNUPUP_DATABASE.id": "score", . .  . .. . }

	class Meta:
		ordering = ('test_unique_id',)