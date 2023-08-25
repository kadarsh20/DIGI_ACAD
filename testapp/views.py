from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.template import Template, Context

# Importing models modules
from loginapp import models as login_models
from courseapp import models as course_models
from testapp import models as test_models

# Importing Security modules.
from django.middleware import csrf

# extra utlities
import datetime
from backend_functions.universal_values import *
import os, json
from digischool.settings import BASE_DIR


def testPage(request):
	if request.POST or len(request.POST) > 0:
		return HttpResponse(f'''<body><script>alert("Some error occured: Incorrect Http Method")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')
	
	# Session and tokens.
	csrf_token = csrf.get_token(request)
	active_status = False
	# getting user_id from session token.
	user_id = None
	if request.session.has_key('user_id'):
		active_status = True
		user_id = request.session["user_id"]

	if active_status:
		extract_user__user_signup_database = login_models.USER_SIGNUP_DATABASE.objects.get(id=user_id)

		if extract_user__user_signup_database.user_category == "TEACHER":
			school_db_teacher_entry = login_models.TEACHER_CODE_MAPPING.objects.get(teacher_email=extract_user__user_signup_database.email_address)
			teached_courses = course_models.AVAILABLE_COURSES.objects.filter(course_instructor= school_db_teacher_entry ) # for now, it will be only one entry.
			
			if not school_db_teacher_entry.activation_status:
				return HttpResponse(f'''<body><script>Some error occured: Maybe the teacher is still not verified, please contact us.</script><meta http-equiv="refresh" content='0; url="/logout/"'/></body>''')
			
			all_course_id = [each_teached_course.course_id for each_teached_course in teached_courses]
		
			test_all_list = [test_models.ALL_TESTS.objects.filter(test_unique_id__contains=each_user_course.course_id) for each_user_course in teached_courses]

			return render(request, "test_teacher.html", { "test_all_list":test_all_list, "all_course_list":all_course_id,  "subject_code": { i: [AVAILABLE_SUBJECTS[i], FULL_NAME[i]] for i in range(len(AVAILABLE_SUBJECTS))}, "current_datetime":datetime.datetime.now()})

		if extract_user__user_signup_database.user_category == "STUDENT":

			selected_user_class = extract_user__user_signup_database.user_class
			selected_user_section = extract_user__user_signup_database.user_section
			generated_unique_id = str(selected_user_class) + str(selected_user_section) + str(OFFERING_YEAR)

			all_course_id = course_models.CLASS_COURSES_MAPPING.objects.get(unique_id=generated_unique_id)
			all_course_id = all_course_id.course_id_array
			all_course_id = all_course_id.strip().split(" ")
			

			user_courses = course_models.AVAILABLE_COURSES.objects.filter(course_id__in=all_course_id)
			all_course_id = { i: all_course_id[i] for i in range(len(all_course_id)) }
			test_all_list = {i:test_models.ALL_TESTS.objects.filter(test_unique_id__contains=each_user_course.course_id) for i, each_user_course in enumerate(user_courses)}
			
			return render(request, "test_student.html", { "test_all_list":test_all_list, "all_course_list":all_course_id,  "subject_code":  { i: [AVAILABLE_SUBJECTS[i], FULL_NAME[i]] for i in range(len(AVAILABLE_SUBJECTS))}, "current_datetime":datetime.datetime.now()})
	else:
		# session is inactive.
		return HttpResponse(f'''<body><meta http-equiv="refresh" content='0; url="/login/"'/></body>''')

def createPage(request, course_id_to_upload):
	if request.POST or len(request.POST) > 0:
		return HttpResponse(f'''<body><script>alert("Some error occured: Incorrect HTTP Request Method.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')
	
	# Session and tokens.
	csrf_token = csrf.get_token(request)
	active_status = False
	# getting user_id from session token.
	user_id = None
	if request.session.has_key('user_id'):
		active_status = True
		user_id = request.session["user_id"]

	extract_user__user_signup_database = login_models.USER_SIGNUP_DATABASE.objects.get(id=user_id)
	if active_status and extract_user__user_signup_database.user_category == "TEACHER":
		school_db_teacher_entry = login_models.TEACHER_CODE_MAPPING.objects.get(teacher_email=extract_user__user_signup_database.email_address)
		teached_courses = course_models.AVAILABLE_COURSES.objects.filter(course_instructor= school_db_teacher_entry ) # for now, it will be only one entry.

		selected_course_id_check = False
		for each_teached_course in teached_courses:
			if each_teached_course.course_id == course_id_to_upload:
				selected_course_id_check = True
				course_in_context = each_teached_course
				break

		if not selected_course_id_check:
			return HttpResponse(f'''<body><script>alert("Some error occured: This is not the course for the current teacher.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')
		
		full_course_name = FULL_NAME[AVAILABLE_SUBJECTS.index(course_id_to_upload[0:2])]

		return render(request, "test_create.html", {"csrf_token" : csrf_token, "course_id":course_id_to_upload,  "full_course_name": full_course_name })
	else:
		# session is inactive or user is not "TEACHER"
		return HttpResponse(f'''<body><script>alert("Unauthorised Access.")</script><meta http-equiv="refresh" content='0; url="/login/"'/></body>''')

def testUploaded(request):
	if request.GET or len(request.GET) > 0:
		return HttpResponse(f'''<body><script>alert("Some error occured: Incorrect HTTP Request Method.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')

	# Session and tokens.
	csrf_token = csrf.get_token(request)
	active_status = False
	# getting user_id from session token.
	user_id = None
	if request.session.has_key('user_id'):
		active_status = True
		user_id = request.session["user_id"]

	extract_user__user_signup_database = login_models.USER_SIGNUP_DATABASE.objects.get(id=user_id)
	if active_status and extract_user__user_signup_database.user_category == "TEACHER":
		school_db_teacher_entry = login_models.TEACHER_CODE_MAPPING.objects.get(teacher_email=extract_user__user_signup_database.email_address)
		teached_courses = course_models.AVAILABLE_COURSES.objects.filter(course_instructor= school_db_teacher_entry ) # for now, it will be only one entry.

		input_data = request.POST

		selected_course_id = request.POST.get("selected_course", "").strip()
		test_title = input_data.get("test_title", "").strip()
		test_instruction = input_data.get("test_instruct", "").strip()
		max_marks = input_data.get("max_marks", float("inf")).strip()
		min_marks = input_data.get("min_marks", -1 * float("inf")).strip()
		test_start_date = input_data.get("start_date").strip()
		test_start_time = input_data.get("start_time").strip()
		test_end_date = input_data.get("end_date").strip()
		test_end_time = input_data.get("end_time").strip()
		

		selected_course_id_check = False
		for each_teached_course in teached_courses:
			if each_teached_course.course_id == selected_course_id:
				selected_course_id_check = True
				course_in_context = each_teached_course
				break

		test_title_check = len(test_title) <= TEST_TITLE_LENGTH and len(test_title) >= 10
		test_instruction_check = len(test_instruction) <= 700 and len(test_instruction) >= 20

		test_start_date_check = True
		try:
			start_year, start_month, start_date = test_start_date.split("-")
			if len(start_year) != 4 or (not start_year.isnumeric()) or len(start_month) != 2 or (not start_month.isnumeric()) or len(start_date) != 2 or (not start_date.isnumeric()):
				raise ValueError
			a = datetime.date(int(start_year), int(start_month), int(start_date))
		except:
			test_start_date_check =False

		test_end_date_check = True
		try:
			end_year, end_month, end_date = test_end_date.split("-")
			if len(end_year) != 4 or (not end_year.isnumeric()) or len(end_month) != 2 or (not end_month.isnumeric()) or len(end_date) != 2 or (not end_date.isnumeric()):
				raise ValueError
			b = datetime.date(int(end_year), int(end_month), int(end_date))
		except:
			test_end_date_check =False


		test_start_time_check=True
		try:
			start_hour, start_minute = test_start_time.split(":")
			if not (2 >= len(start_hour) >= 1) or (not start_hour.isnumeric()) or not (2 >= len(start_minute) >= 1) or (not start_minute.isnumeric()):
				raise ValueError
			c = datetime.time(int(start_hour), int(start_minute))
		except:
			test_start_time_check=False

		test_end_time_check=True
		try:
			end_hour, end_minute = test_end_time.split(":")
			if not (2 >= len(end_hour) >= 1) or (not end_hour.isnumeric()) or not (2 >= len(end_minute) >= 1) or (not end_minute.isnumeric()):
				raise ValueError
			d = datetime.time(int(end_hour), int(end_minute))
		except:
			test_end_time_check=False

		max_marks_check= max_marks.isnumeric() and 1 <= len(max_marks) < 4
		min_marks_check = min_marks.isnumeric() and 1 <= len(min_marks) < 4


		if request.FILES:
			test_files = request.FILES.get("test-files", None)
		else:
			test_files = None

		test_files_check = True
		if test_files:
			if len(test_files.name.strip()) > 100 or len(test_files.name.strip()) < 6:
				test_files_check = False
			reverse_file_name = test_files.name.strip()[::-1]
			file_extension = ""
			for char in reverse_file_name:
				file_extension += char
				if char == ".":
					break
			file_extension = file_extension[::-1]
			if not (file_extension in ALLOWED_FILE_TYPE):
				test_files_check = False


		test_questions_json = dict()
		i = 1
		while i <= MAX_QUESTIONS:
			question_i = input_data.get(f"question-{i}", False)
			
			if not question_i or 500 < len(question_i) < 10:
				i = i + 1
				continue
			else:
				test_questions_json[str(i)] = str(question_i).strip()
			i = i + 1

		if not (selected_course_id_check and test_title_check and test_instruction_check and test_start_date_check and test_start_time_check and test_end_date_check and test_end_time_check and test_files_check and len(test_questions_json) >= 1):
			return HttpResponse(f'''<body><script>alert("Some error occured: some inputs were invalid.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')

		# datetime(year, month, day, hour, minute, second, microsecond).
		start_datetime = datetime.datetime(int(start_year), int(start_month), int(start_date), int(start_hour), int(start_minute), 0, 0)
		end_datetime = datetime.datetime(int(end_year), int(end_month), int(end_date), int(end_hour), int( end_minute), 0, 0)
		

		test_series_number_new = course_in_context.test_series_number + 1

		if test_series_number_new >= 100:
			return HttpResponse(f'''<body><script>alert("Maximum Limit of Test is reached. Please contact us.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')
		
		course_in_context.test_series_number = test_series_number_new
		course_in_context.save()

		test_unique_id = str(selected_course_id) + (str(test_series_number_new) if len(str(test_series_number_new)) == 2 else "0" + str(test_series_number_new))

		try:
			question_file_name = os.path.join(BASE_DIR, f"Question/{test_unique_id}.json")
			question_file = open(question_file_name, "w")
			a = json.dump(test_questions_json, question_file)
			question_file.close()
		except:
			return HttpResponse(f'''<body><script>alert("Some error occured. Server side error. Please try again later or contact us.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')

		try:
			question_data_file_name = os.path.join(BASE_DIR, f"Question/{test_unique_id}-data.json")
			question_data_file = open(question_data_file_name, "w")
			b = json.dump({"MAXIMUM MARKS": max_marks, "MINIMUM MARKS": min_marks}, question_data_file)
			question_data_file.close()

		except:
			return HttpResponse(f'''<body><script>alert("Some error occured. Server side error. Please try again later or contact us.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')

		try:
			setting_test = test_models.ALL_TESTS(test_title = test_title, test_instruction = test_instruction, start_datetime =start_datetime, end_datetime=end_datetime, files=test_files, test_unique_id= test_unique_id, course_mapping = course_in_context, test_questions=question_file_name, test_data=question_data_file_name)
			setting_test.save()
		except:
			"""----------Some error while setting test.---------------"""
			test_series_number_new = max(course_in_context.test_series_number - 1, 0)
			course_in_context.test_series_number = test_series_number_new
			course_in_context.save()
			return HttpResponse(f'''<body><script>alert("Some error occured: Server issue. Please try again later. If issue persists contact us.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')
		
		"""----------test Succesfully Created.---------------"""
		return HttpResponse(f'''<body><script>alert("Test is sccessfully created!!")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')
	else:
		# session is inactive or user is not "TEACHER"
		return HttpResponse(f'''<body><script>alert("Unauthorised Access.")</script><meta http-equiv="refresh" content='0; url="/login/"'/></body>''')


def eachTestView(request, given_unique_id):
	if request.POST or len(request.POST) > 0:
		return HttpResponse(f'''<body><script>alert("Some error occured: Incorrect HTTP Request Method.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')
		
	# Session and tokens.
	csrf_token = csrf.get_token(request)
	active_status = False

	# getting user_id from session token.
	user_id = None
	if request.session.has_key('user_id'):
		active_status = True
		user_id = request.session["user_id"]

	if active_status:
		extract_user__user_signup_database = login_models.USER_SIGNUP_DATABASE.objects.get(id=user_id)

		if extract_user__user_signup_database.user_category == "TEACHER":
			school_db_teacher_entry = login_models.TEACHER_CODE_MAPPING.objects.get(teacher_email=extract_user__user_signup_database.email_address)
			teached_courses = course_models.AVAILABLE_COURSES.objects.filter(course_instructor= school_db_teacher_entry ) # for now, it will be only one entry.

			autheticated = False
			for each_teached_course in teached_courses:
				all_test_list_in_a_course = test_models.ALL_TESTS.objects.filter(test_unique_id__contains=each_teached_course.course_id)
				for each_test_in_course in all_test_list_in_a_course:
					if each_test_in_course.test_unique_id == given_unique_id:
						autheticated = True
						selected_test = each_test_in_course
						course_in_context = each_teached_course
						break

			if not autheticated:
				return HttpResponse(f'''<body><script>alert("Unauthorised Access.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')
			try:
				test_questions_file_name = selected_test.test_questions
				test_questions_file = open(test_questions_file_name, "r")
				test_questions = json.load(test_questions_file)
				test_questions_file.close()
			except:
				return HttpResponse(f'''<body><script>alert("Some error occured, maybe the test is deleted. Contact us.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')	

			test_end_time = selected_test.end_datetime.strftime("%d/%m/%Y %H:%M:%S")
			return render(request, "test_each_page_teacher.html", {"csrf_token": csrf_token, "given_test":selected_test, "test_questions":test_questions, 'current_datetime':datetime.datetime.now(), "test_end_time":test_end_time})

		if extract_user__user_signup_database.user_category == "STUDENT":
			selected_user_class = extract_user__user_signup_database.user_class
			selected_user_section = extract_user__user_signup_database.user_section
			generated_unique_id = selected_user_class + selected_user_section + str(OFFERING_YEAR)

			all_course_id = course_models.CLASS_COURSES_MAPPING.objects.get(unique_id=generated_unique_id)
			all_course_id = all_course_id.course_id_array
			all_course_id = all_course_id.strip().split(" ")

			autheticated = False
			for each_course_id in all_course_id:
				each_course = course_models.AVAILABLE_COURSES.objects.get(course_id=each_course_id)
				all_test_list_in_a_course = test_models.ALL_TESTS.objects.filter(test_unique_id__contains=each_course.course_id)
				for each_test_in_course in all_test_list_in_a_course:
					if each_test_in_course.test_unique_id == given_unique_id:
						autheticated = True
						selected_test = each_test_in_course
						course_in_context = each_course
						break

			if not autheticated:
				return HttpResponse(f'''<body><script>alert("Unauthorised Access.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')	
			
			try:
				test_questions_file_name = selected_test.test_questions
				test_answer_file_name = selected_test.test_data
				test_questions_file = open(test_questions_file_name, "r")
				test_answer_file = open(test_answer_file_name,"r")
				test_questions = json.load(test_questions_file)
				test_answer = json.load(test_answer_file)
				test_questions_file.close()
				test_answer_file.close()
			except:
				return HttpResponse(f'''<body><script>alert("Some error occured, maybe the test is deleted. Contact us.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')	

			submit_status = False
			student_answer_file_name = test_answer.get(str(extract_user__user_signup_database.id), False)
			student_answer = {"SCORE":float("inf")}

			if student_answer_file_name:

				try:
					student_answer_file = open(student_answer_file_name, "r")
					student_answer = json.load(student_answer_file)
					student_answer_file.close()
				except:
					return HttpResponse(f'''<body><script>alert("Some error occured, maybe the answer is deleted. Contact us.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')	

				submit_status = True
			test_end_time = selected_test.end_datetime.strftime("%d/%m/%Y %H:%M:%S")

			return render(request, "test_each_page.html", {"csrf_token": csrf_token, "submit_status":submit_status, "given_test":selected_test, "test_end_time": test_end_time, 'current_datetime':datetime.datetime.now(), "test_questions": test_questions, "student_answer":student_answer})
	else:
		# session is inactive.
		return HttpResponse(f'''<body><meta http-equiv="refresh" content='0; url="/login/"'/></body>''')



def editTestPage(request, test_unique_id):
	if request.POST or len(request.POST) > 0:
		return HttpResponse(f'''<body><script>alert("Some error occured: Incorrect HTTP Request Method.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')
	
	# Session and tokens.
	csrf_token = csrf.get_token(request)
	active_status = False
	# getting user_id from session token.
	user_id = None
	if request.session.has_key('user_id'):
		active_status = True
		user_id = request.session["user_id"]

	extract_user__user_signup_database = login_models.USER_SIGNUP_DATABASE.objects.get(id=user_id)
	if active_status and extract_user__user_signup_database.user_category == "TEACHER":
		school_db_teacher_entry = login_models.TEACHER_CODE_MAPPING.objects.get(teacher_email=extract_user__user_signup_database.email_address)
		teached_courses = course_models.AVAILABLE_COURSES.objects.filter(course_instructor= school_db_teacher_entry ) # for now, it will be only one entry.

		autheticated = False
		for each_teached_course in teached_courses:
			all_test_list_in_a_course = test_models.ALL_TESTS.objects.filter(test_unique_id__contains=each_teached_course.course_id)
			for each_test_in_course in all_test_list_in_a_course:
				if each_test_in_course.test_unique_id == test_unique_id:
					autheticated = True
					selected_test = each_test_in_course
					course_in_context = each_teached_course
					break

		if not autheticated:
				return HttpResponse(f'''<body><script>alert("Unauthorised Access.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')
		
		full_course_name = FULL_NAME[AVAILABLE_SUBJECTS.index(test_unique_id[0:2])]

		return render(request, "test_edit.html", {"csrf_token": csrf_token, "test_unique_id": test_unique_id, "full_course_name": full_course_name })
	else:
		# session is inactive or user is not "TEACHER"
		return HttpResponse(f'''<body><script>alert("Unauthorised Access.")</script><meta http-equiv="refresh" content='0; url="/login/"'/></body>''')


def editTestUpload(request, test_unique_id):
	if request.GET or len(request.GET) > 0:
		return HttpResponse(f'''<body><script>alert("Some error occured: Incorrect HTTP Request Method.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')

	# Session and tokens.
	csrf_token = csrf.get_token(request)
	active_status = False
	# getting user_id from session token.
	user_id = None
	if request.session.has_key('user_id'):
		active_status = True
		user_id = request.session["user_id"]

	extract_user__user_signup_database = login_models.USER_SIGNUP_DATABASE.objects.get(id=user_id)
	if active_status and extract_user__user_signup_database.user_category == "TEACHER":
		
		school_db_teacher_entry = login_models.TEACHER_CODE_MAPPING.objects.get(teacher_email=extract_user__user_signup_database.email_address)
		teached_courses = course_models.AVAILABLE_COURSES.objects.filter(course_instructor= school_db_teacher_entry ) # for now, it will be only one entry.

		input_data = request.POST

		edit_test_title = input_data.get("test_title", "").strip()
		edit_test_instruction = input_data.get("test_instruct", "").strip()
		edit_max_marks = input_data.get("max_marks", float("inf")).strip()
		edit_min_marks = input_data.get("min_marks", -1 * float("inf")).strip()
		edit_test_start_date = input_data.get("start_date").strip()
		edit_test_start_time = input_data.get("start_time").strip()
		edit_test_end_date = input_data.get("end_date").strip()
		edit_test_end_time = input_data.get("end_time").strip()

		autheticated = False
		for each_teached_course in teached_courses:
			all_test_list_in_a_course = test_models.ALL_TESTS.objects.filter(test_unique_id__contains=each_teached_course.course_id)
			for each_test_in_course in all_test_list_in_a_course:
				if each_test_in_course.test_unique_id == test_unique_id:
					autheticated = True
					selected_test = each_test_in_course
					course_in_context = each_teached_course
					break

		edit_test_title_check = len(edit_test_title) <= TEST_TITLE_LENGTH and len(edit_test_title) >= 10
		edit_test_instruction_check = len(edit_test_instruction) <= 700 and len(edit_test_instruction) >= 20

		edit_test_start_date_check = True
		try:
			start_year, start_month, start_date = edit_test_start_date.split("-")
			if len(start_year) != 4 or (not start_year.isnumeric()) or len(start_month) != 2 or (not start_month.isnumeric()) or len(start_date) != 2 or (not start_date.isnumeric()):
				raise ValueError
			a = datetime.date(int(start_year), int(start_month), int(start_date))
		except:
			edit_test_start_date_check = False


		edit_test_end_date_check = True
		try:
			end_year, end_month, end_date = edit_test_end_date.split("-")
			if len(end_year) != 4 or (not end_year.isnumeric()) or len(end_month) != 2 or (not end_month.isnumeric()) or len(end_date) != 2 or (not end_date.isnumeric()):
				raise ValueError
			b = datetime.date(int(end_year), int(end_month), int(end_date))
		except:
			edit_test_end_date_check =False


		edit_test_start_time_check=True
		try:
			start_hour, start_minute = edit_test_start_time.split(":")
			if not (2 >= len(start_hour) >= 1) or (not start_hour.isnumeric()) or not (2 >= len(start_minute) >= 1) or (not start_minute.isnumeric()):
				raise ValueError
			c = datetime.time(int(start_hour), int(start_minute))
		except:
			edit_test_start_time_check=False

		edit_test_end_time_check=True
		try:
			end_hour, end_minute = edit_test_end_time.split(":")
			if not (2 >= len(end_hour) >= 1) or (not end_hour.isnumeric()) or not (2 >= len(end_minute) >= 1) or (not end_minute.isnumeric()):
				raise ValueError
			d = datetime.time(int(end_hour), int(end_minute))
		except:
			edit_test_end_time_check=False

		edit_max_marks_check= edit_max_marks.isnumeric() and 1 <= len(edit_max_marks) < 4
		edit_min_marks_check = edit_min_marks.isnumeric() and 1 <= len(edit_min_marks) < 4

		if request.FILES:
			edit_test_files = request.FILES.get("test-files", None)
		else:
			edit_test_files = None

		edit_test_files_check = True
		if edit_test_files:
			# lecture files are not compulsory.
			if len(edit_test_files.name.strip()) > 100 or len(edit_test_files.name.strip()) < 6:
				edit_test_files_check = False
			reverse_file_name = edit_test_files.name.strip()[::-1]
			file_extension = ""
			for char in reverse_file_name:
				file_extension += char
				if char == ".":
					break
			file_extension = file_extension[::-1]
			if not (file_extension in ALLOWED_FILE_TYPE):
				edit_test_files_check = False


		dump_status = input_data.get("dump_status", None).strip()
		dump_status_check = False
		if dump_status == "yes" or dump_status == "no":
			dump_status_check = True

		test_questions_json = dict()
		i = 1
		while i <= MAX_QUESTIONS:
			question_i = input_data.get(f"question-{i}", False)
			
			if not question_i or 500 < len(question_i) < 10:
				i = i + 1
				continue
			else:
				test_questions_json[str(i)] = str(question_i).strip()
			i = i + 1

		if not (autheticated and edit_test_title_check and edit_test_instruction_check and edit_test_start_date_check and edit_test_start_time_check and edit_test_end_date_check and edit_test_end_time_check and edit_test_files_check and dump_status_check):
			return HttpResponse(f'''<body><script>alert("Some error occured: some inputs were invalid.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')
		
		# datetime(year, month, day, hour, minute, second, microsecond.
		edit_start_datetime = datetime.datetime(int(start_year), int(start_month), int(start_date), int(start_hour), int(start_minute), 0, 0)
		edit_end_datetime = datetime.datetime(int(end_year), int(end_month), int(end_date), int(end_hour), int( end_minute), 0, 0)
		
		try:
			question_file_name = selected_test.test_questions
			question_file = open(question_file_name, "w")
			a = json.dump(test_questions_json, question_file)
			question_file.close()
		except:
			return HttpResponse(f'''<body><script>alert("Some error occured. Server side error. Please try again later or contact us.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')
		
		try:
			question_data_file_name = selected_test.test_data
			question_data_file = open(question_data_file_name, "w")
			
			if dump_status == "yes":
				b = json.dump({"MAXIMUM MARKS": edit_max_marks, "MINIMUM MARKS": edit_min_marks}, question_data_file)
			else:
				c = json.load(question_data_file)
				c["MAXIMUM MARKS"] = edit_max_marks
				c["MINIMUM MARKS"] = edit_min_marks
				b = json.dump(c, question_data_file)
			question_data_file.close()
		except:
			return HttpResponse(f'''<body><script>alert("Some error occured. Server side error. Please try again later or contact us.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')


		try:
			updating_test = test_models.ALL_TESTS.objects.get(test_unique_id=test_unique_id)
			updating_test.test_title = edit_test_title
			updating_test.test_instruction = edit_test_instruction
			updating_test.start_datetime = edit_start_datetime
			updating_test.end_datetime = edit_end_datetime
			updating_test.files = edit_test_files
			updating_test.save()
		except:
			"""----------Some error while setting test.---------------"""
			return HttpResponse(f'''<body><script>alert("Some error occured: Server issue. Please try again later. If issue persists contact us.")</script><meta http-equiv="refresh" content='0; url="/test/view/{test_unique_id}"'/></body>''')
		
		"""----------test Succesfully Created.---------------"""
		return HttpResponse(f'''<body><script>alert("Test is sccessfully Edited!!")</script><meta http-equiv="refresh" content='0; url="/test/view/{test_unique_id}"'/></body>''')
	else:
		# session is inactive or user is not "TEACHER"
		return HttpResponse(f'''<body><script>alert("Unauthorised Access.")</script><meta http-equiv="refresh" content='0; url="/login/"'/></body>''')


def answerUpload(request, test_unique_id):
	if request.GET or len(request.GET) > 0:
		return HttpResponse(f'''<body><script>alert("Some error occured: Incorrect HTTP Request Method.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')

	# Session and tokens.
	csrf_token = csrf.get_token(request)
	active_status = False
	# getting user_id from session token.
	user_id = None
	if request.session.has_key('user_id'):
		active_status = True
		user_id = request.session["user_id"]

	extract_user__user_signup_database = login_models.USER_SIGNUP_DATABASE.objects.get(id=user_id)
	if active_status and extract_user__user_signup_database.user_category == "STUDENT":
		selected_user_class = extract_user__user_signup_database.user_class
		selected_user_section = extract_user__user_signup_database.user_section
		generated_unique_id = selected_user_class + selected_user_section + str(OFFERING_YEAR)

		all_course_id = course_models.CLASS_COURSES_MAPPING.objects.get(unique_id=generated_unique_id)
		all_course_id = all_course_id.course_id_array
		all_course_id = all_course_id.strip().split(" ")


		autheticated = False
		for each_course_id in all_course_id:
			each_course = course_models.AVAILABLE_COURSES.objects.get(course_id=each_course_id)
			all_test_list_in_a_course = test_models.ALL_TESTS.objects.filter(test_unique_id__contains=each_course.course_id)
			for each_test_in_course in all_test_list_in_a_course:
				if each_test_in_course.test_unique_id == test_unique_id:
					autheticated = True
					selected_test = each_test_in_course
					course_in_context = each_course
					break

		current_datetime = datetime.datetime.now()
		if selected_test.start_datetime.timestamp() > current_datetime.timestamp() or selected_test.end_datetime.timestamp() < current_datetime.timestamp():
			autheticated = False

		if not autheticated:
			return HttpResponse(f'''<body><script>alert("Unauthorised Access and/or Test is "too soon to open" or Test is "already over".")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')


		test_answer_file_name = selected_test.test_data
		test_answer_file = open(test_answer_file_name,"r")
		test_answer = json.load(test_answer_file)

		student_answer_file_name = test_answer.get(str(extract_user__user_signup_database.id), False)
		test_answer_file.close()

		if student_answer_file_name:
			return HttpResponse(f'''<body><script>alert("Test is already submitted.")</script><meta http-equiv="refresh" content='0; url="/test/view/{test_unique_id}"'/></body>''')

		input_data = request.POST
		
		test_questions_file_name = selected_test.test_questions
		test_answer_file_name = selected_test.test_data
		test_questions_file = open(test_questions_file_name, "r")
		test_answer_file = open(test_answer_file_name,"r")
		test_questions = json.load(test_questions_file)
		test_answer = json.load(test_answer_file)

		student_answer = {"SCORE":float("inf")}

		for test_number_key in test_questions:
			answer_for_test_number = input_data.get(f"{test_number_key}-answer", "")
			answer_check = len(answer_for_test_number) > 1 and len(answer_for_test_number) < 10000
			student_answer[test_number_key] = answer_for_test_number if answer_check else ""
	
		test_questions_file.close()
		test_answer_file.close()
		
		try:
			file_name = os.path.join(BASE_DIR, f"Answer/{test_unique_id}-{extract_user__user_signup_database.id}.json")
			student_file = open(file_name, "w")
			a = json.dump(student_answer, student_file)
			student_file.close()
			
			test_answer[extract_user__user_signup_database.id] = str(file_name)

			test_answer_file = open(test_answer_file_name, "w")
			a = json.dump(test_answer, test_answer_file)
			test_answer_file.close()
		except:
			return HttpResponse(f'''<body><script>alert("There was an error while submission. If time is there please upload the answer again. Else contact teacher.")</script><meta http-equiv="refresh" content='0; url="/test/view/{test_unique_id}"'/></body>''')

		return HttpResponse(f'''<body><script>alert("Test is successfully submitted.")</script><meta http-equiv="refresh" content='0; url="/test/view/{test_unique_id}"'/></body>''')

def answerCheckPage(request, test_unique_id):
	if request.POST or len(request.POST) > 0:
		return HttpResponse(f'''<body><script>alert("Some error occured: Incorrect HTTP Request Method.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')

	# Session and tokens.
	csrf_token = csrf.get_token(request)
	active_status = False
	# getting user_id from session token.
	user_id = None
	if request.session.has_key('user_id'):
		active_status = True
		user_id = request.session["user_id"]

	extract_user__user_signup_database = login_models.USER_SIGNUP_DATABASE.objects.get(id=user_id)
	if active_status and extract_user__user_signup_database.user_category == "TEACHER":
		school_db_teacher_entry = login_models.TEACHER_CODE_MAPPING.objects.get(teacher_email=extract_user__user_signup_database.email_address)
		teached_courses = course_models.AVAILABLE_COURSES.objects.filter(course_instructor= school_db_teacher_entry ) # for now, it will be only one entry.

		autheticated = False
		for each_teached_course in teached_courses:
			all_test_list_in_a_course = test_models.ALL_TESTS.objects.filter(test_unique_id__contains=each_teached_course.course_id)
			for each_test_in_course in all_test_list_in_a_course:
				if each_test_in_course.test_unique_id == test_unique_id:
					autheticated = True
					selected_test = each_test_in_course
					course_in_context = each_teached_course
					break

		if not autheticated:
				return HttpResponse(f'''<body><script>alert("Unauthorised Access.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')
		
		# need to change when the html file is created.
		return render(request, "test_answer.html", {"csrf_token": csrf_token, "user_signup_db": login_models.USER_SIGNUP_DATABASE , "given_test":selected_test})
	else:
		# session is inactive or user is not "TEACHER"
		return HttpResponse(f'''<body><script>alert("Unauthorised Access.")</script><meta http-equiv="refresh" content='0; url="/login/"'/></body>''')

def scoreUpload(request, test_unique_id):
	if request.GET or len(request.GET) > 0:
		return HttpResponse(f'''<body><script>alert("Some error occured: Incorrect HTTP Request Method.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')

	# Session and tokens.
	csrf_token = csrf.get_token(request)
	active_status = False
	# getting user_id from session token.
	user_id = None
	if request.session.has_key('user_id'):
		active_status = True
		user_id = request.session["user_id"]

	extract_user__user_signup_database = login_models.USER_SIGNUP_DATABASE.objects.get(id=user_id)
	if active_status and extract_user__user_signup_database.user_category == "TEACHER":
		
		school_db_teacher_entry = login_models.TEACHER_CODE_MAPPING.objects.get(teacher_email=extract_user__user_signup_database.email_address)
		teached_courses = course_models.AVAILABLE_COURSES.objects.filter(course_instructor= school_db_teacher_entry ) # for now, it will be only one entry.

		autheticated = False
		for each_teached_course in teached_courses:
			all_test_list_in_a_course = test_models.ALL_TESTS.objects.filter(test_unique_id__contains=each_teached_course.course_id)
			for each_test_in_course in all_test_list_in_a_course:
				if each_test_in_course.test_unique_id == test_unique_id:
					autheticated = True
					selected_test = each_test_in_course
					course_in_context = each_teached_course
					break

		if not autheticated:
			return HttpResponse(f'''<body><script>alert("Unauthorised Access.")</script><meta http-equiv="refresh" content='0; url="/test/"'/></body>''')
		
		input_data = request.POST

		def check_if_valid_student(sid, req_class, req_section):
			db = login_models.USER_SIGNUP_DATABASE.get(id=sid)
			status = False
			try:
				is_int = int(sid)
				return db.user_class == req_class and db.user_section == req_section
			except:
				return False
		
		data_correct = True
		incorrect_count = 0
		try:
			for student_id in input_data:
				status_each = check_if_valid_student(student_id, test_unique_id[2:4], test_unique_id[4:6])
				if status_each:
					selected_test.test_data[student_id]["SCORE"] = input_data[student_id]
				else:
					data_correct = False
					incorrect_count += 1
			selected_test.save()
		except:
			return HttpResponse(f'''<body><script>alert("Some error occured: Server issue. Please try again later. If issue persists contact us.")</script><meta http-equiv="refresh" content='0; url="/test/answer/{test_unique_id}"'/></body>''')
		
		if not data_correct:
			return HttpResponse(f'''<body><script>alert("Some marks were not valid ({incorrect_count} entries.), only partial entries are added.")</script><meta http-equiv="refresh" content='0; url="/test/answer/{test_unique_id}"'/></body>''')

		return HttpResponse(f'''<body><script>alert("Marks are successfully added!")</script><meta http-equiv="refresh" content='0; url="/test/answer/{test_unique_id}"'/></body>''')
	else:
		# session is inactive or user is not "TEACHER"
		return HttpResponse(f'''<body><script>alert("Unauthorised Access.")</script><meta http-equiv="refresh" content='0; url="/login/"'/></body>''')