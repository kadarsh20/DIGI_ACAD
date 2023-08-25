from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.template import Template, Context

# Importing models modules
from loginapp import models as login_models
from profileapp import models as profile_models
from courseapp import models as course_models
from testapp import models as test_models

# Importing Security modules.
from django.middleware import csrf

# extra utilities.
import datetime
from backend_functions.universal_values import *
from backend_functions import backend_handling_functions
from loginapp import validation_check
from digischool.settings import MEDIA_URL
def profilePage(request):
	if request.POST or len(request.POST) > 0:
		return HttpResponse(f'''<body><script>alert("Some error occured: Incorrect Http Method")</script><meta http-equiv="refresh" content='0; url="/profile/"'/></body>''')
	
	# Session and tokens.
	csrf_token = csrf.get_token(request)
	active_status = False
	# getting user_id from session token.
	user_id = None
	if request.session.has_key('user_id'):
		active_status = True
		user_id = request.session["user_id"]

	extract_user__user_signup_database = login_models.USER_SIGNUP_DATABASE.objects.get(id=user_id)
	if active_status:
		if extract_user__user_signup_database.user_category == "TEACHER":
			school_db_teacher_entry = login_models.TEACHER_CODE_MAPPING.objects.get(teacher_email=extract_user__user_signup_database.email_address)
			teached_courses = course_models.AVAILABLE_COURSES.objects.filter(course_instructor= school_db_teacher_entry ) # for now, it will be only one entry.
			
			if not school_db_teacher_entry.activation_status:
				return HttpResponse(f'''<body><script>alert("Some error occured: Maybe the teacher is still not verified, please contact us.")</script><meta http-equiv="refresh" content='0; url="/logout/"'/></body>''')
			
			all_course_id = [each_teached_course.course_id for each_teached_course in teached_courses]
	
			test_all_answer_list = dict()
			for i, each_user_course in enumerate(teached_courses):
			 	test_in_a_subject = test_models.ALL_TESTS.objects.filter(test_unique_id__contains=each_user_course.course_id)
			 	av_list = list()
			 	indi_list = list()
			 	name_list = list()
			 	for test_each in test_in_a_subject:
			 		test_number = test_each.test_unique_id[10:]
			 		test_name = 'Test-' + test_number
			 		av, indi =	backend_handling_functions.returnStats(test_each, 0)
			 		av_list.append(av)
			 		indi_list.append(indi)
			 		name_list.append(test_name)
			 	test_all_answer_list[i] = [av_list, indi_list, name_list]
			
			extract_user__user_profile_database = profile_models.USER_PROFILE_DATABASE.objects.get(user_signup_db_mapping=extract_user__user_signup_database)
			profile_data = extract_user__user_profile_database

			return render(request, "profile_page_teacher.html", {"MEDIA_URL":MEDIA_URL,"profile_data":profile_data,"user_data" : profile_models.USER_PROFILE_DATABASE.objects.filter(user_signup_db_mapping=extract_user__user_signup_database)[0],  "all_course_list":all_course_id,  "subject_code": { i: [AVAILABLE_SUBJECTS[i], FULL_NAME[i]] for i in range(len(AVAILABLE_SUBJECTS))}, "current_datetime":datetime.datetime.now()})

		if extract_user__user_signup_database.user_category == "STUDENT":
			selected_user_class = extract_user__user_signup_database.user_class
			selected_user_section = extract_user__user_signup_database.user_section
			generated_unique_id = str(selected_user_class) + str(selected_user_section) + str(OFFERING_YEAR)

			all_course_id = course_models.CLASS_COURSES_MAPPING.objects.get(unique_id=generated_unique_id)
			all_course_id = all_course_id.course_id_array
			all_course_id = all_course_id.strip().split(" ")
			all_course_id = { i: all_course_id[i] for i in range(len(all_course_id)) }

			user_courses = course_models.AVAILABLE_COURSES.objects.filter(course_id__in=all_course_id)

			test_all_answer_list = dict()
			for i, each_user_course in enumerate(user_courses):
			 	test_in_a_subject = test_models.ALL_TESTS.objects.filter(test_unique_id__contains=each_user_course.course_id)
			 	av_list = list()
			 	indi_list = list()
			 	name_list = list()
			 	for test_each in test_in_a_subject:
			 		test_number = test_each.test_unique_id[10:]
			 		test_name = 'Test-' + test_number
			 		av, indi =	backend_handling_functions.returnStats(test_each, extract_user__user_signup_database.id)
			 		av_list.append(av)
			 		indi_list.append(indi)
			 		name_list.append(test_name)
			 	test_all_answer_list[i] = [av_list, indi_list, name_list]

			extract_user__user_profile_database = profile_models.USER_PROFILE_DATABASE.objects.get(user_signup_db_mapping=extract_user__user_signup_database)
			profile_data = extract_user__user_profile_database
			return render(request, "profile_page_student.html", {"MEDIA_URL":MEDIA_URL,"test_all_answer_list":test_all_answer_list, "all_course_list":all_course_id,  "subject_code":  { i: [AVAILABLE_SUBJECTS[i], FULL_NAME[i]] for i in range(len(AVAILABLE_SUBJECTS))}, "current_datetime":datetime.datetime.now(),"user_data" : profile_data})
		# session is inactive.
		return HttpResponse(f'''<body><meta http-equiv="refresh" content='0; url="/login/"'/></body>''')
		
def editProfilePage(request):
	if request.POST or len(request.POST) > 0:
		return HttpResponse(f'''<body><script>alert("Some error occured: Incorrect Http Method")</script><meta http-equiv="refresh" content='0; url="/profile/"'/></body>''')
	
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
		extract_user__user_profile_database = profile_models.USER_PROFILE_DATABASE.objects.get(user_signup_db_mapping=extract_user__user_signup_database)

		if not extract_user__user_profile_database.edit_once:
			if extract_user__user_signup_database.user_category == "TEACHER":
				return render(request, "edit_profile_teacher_page.html", {"MEDIA_URL":MEDIA_URL,"profile_data":extract_user__user_profile_database,"csrf_token":csrf_token})
			if extract_user__user_signup_database.user_category == "STUDENT":
				return render(request, "edit_profile_student_page.html", {"MEDIA_URL":MEDIA_URL,"profile_data":extract_user__user_profile_database,"csrf_token":csrf_token})
		else:
			return render(request, "edit_page_not_allowed.html", {"user_category":extract_user__user_signup_database.user_category, "preview_user": extract_user__user_signup_database, "preview_profile": extract_user__user_profile_database})

	else:
		# session is inactive.
		return HttpResponse(f'''<body><meta http-equiv="refresh" content='0; url="/login/"'/></body>''')

def editProfilePagePosted(request):
	if request.GET or len(request.GET) > 0:
		return HttpResponse(f'''<body><script>alert("Some error occured: Incorrect Http Method")</script><meta http-equiv="refresh" content='0; url="/profile/"'/></body>''')
	
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
		extract_user__user_profile_database = profile_models.USER_PROFILE_DATABASE.objects.get(user_signup_db_mapping=extract_user__user_signup_database)
		
		if not extract_user__user_profile_database.edit_once:
			if extract_user__user_signup_database.user_category == "STUDENT":
				
				input_data = request.POST

				other_error = False

				edit_full_name = input_data.get("edit_name", "").strip().lower().split()
				try:
					edit_first_name, edit_last_name = edit_full_name[0], edit_full_name[1]
					first_name_check = validation_check.nameCheck(edit_first_name)
					last_name_check = validation_check.nameCheck(edit_last_name)
				except:
					other_error = True

				edit_class, edit_section = input_data.get("edit_class", "0").strip(), input_data.get("edit_section", "NaN").strip()
				user_class_check = validation_check.classCheck(edit_class)
				user_section_check = validation_check.sectionCheck(edit_section)

				edit_contact, edit_r_number = input_data.get("edit_contact", "0").strip(), input_data.get("edit_r_number", "0").strip()
				contact_check = validation_check.contactCheck(edit_contact)
				r_number_check = validation_check.rCheck(edit_r_number)


				edit_school_name = input_data.get("edit_school", "").strip()
				school_name_check = validation_check.schoolNameCheck(edit_school_name)

				father_name, mother_name = input_data.get("father_name", "").strip().lower().split(), input_data.get("mother_name", "").strip().lower().split()
				try:
					father_name_check = validation_check.nameCheck(father_name[0]) and validation_check.nameCheck(father_name[1])
					mother_name_check = validation_check.nameCheck(mother_name[0]) and validation_check.nameCheck(mother_name[1])
				except:
					if len(father_name) == 1:
						father_name.append(edit_last_name)
					else:
						other_error = True
					if len(mother_name) == 1:
						mother_name.append(edit_last_name)
					else:
						other_error = True

				if request.FILES:
					image_file = request.FILES.get("imagefile",None)
				else:
					image_file = None
				image_files_check = True
				if image_file:
					# lecture files are not compulsory.
					if len(image_file.name.strip()) > 100 or len(image_file.name.strip()) < 6:
						image_files_check = False
					reverse_file_name = image_file.name.strip()[::-1]
					file_extension = ""
					for char in reverse_file_name:
						file_extension += char
						if char == ".":
							break
					file_extension = file_extension[::-1]
					if not (file_extension in ALLOWED_IMAGE_FILE_TYPE):
						image_files_check = False



				if not ((not other_error) and first_name_check and last_name_check and user_class_check and user_section_check and contact_check and r_number_check and school_name_check and father_name_check and mother_name_check and image_files_check):
					# handling tempered data.
					# The incoming data was corrupted (maybe using burpsuite.) (This is because, all the above validations were done at frontend, but still the value arent valid values.)
					return render(request, 'edit_profile_student_page.html', {"MEDIA_URL":MEDIA_URL,"csrf_token": csrf_token , "error_edit" : True})

				"""----------Now all the input values are valid.---------------"""

				# data formatting.
				edit_first_name = edit_first_name[0].upper() + edit_first_name[1:]
				edit_last_name = edit_last_name[0].upper() + edit_last_name[1:]
				edit_section = edit_section.upper() + "S"
				if len(edit_class) != 2:
					edit_class = "0" + edit_class
				father_name = father_name[0][0].upper() + father_name[0][1:] + " " + father_name[1][0].upper() + father_name[1][1:]
				mother_name = mother_name[0][0].upper() + mother_name[0][1:] + " " + mother_name[1][0].upper() + mother_name[1][1:]


				# backend database working
				class_course_field = backend_handling_functions.auto_assign_course(edit_class, edit_section, "STUDENT")

				try:
					extract_user__user_signup_database.first_name = edit_first_name
					extract_user__user_signup_database.last_name = edit_last_name
					extract_user__user_signup_database.user_class = edit_class
					extract_user__user_signup_database.user_section = edit_section
					extract_user__user_signup_database.user_contact = edit_contact 
					extract_user__user_signup_database.user_r_number = edit_r_number
					extract_user__user_signup_database.school_name = edit_school_name
					extract_user__user_signup_database.save()

					extract_user__user_profile_database.user_signup_db_mapping = extract_user__user_signup_database
					extract_user__user_profile_database.father_name = father_name
					extract_user__user_profile_database.mother_name = mother_name
					extract_user__user_profile_database.edit_once = True
					extract_user__user_profile_database.user_profile_photo = image_file
					extract_user__user_profile_database.save()
				except:
					"""----------Some error while setting.---------------"""
					extract_user__user_profile_database.edit_once = False
					extract_user__user_profile_database.save()
					return render(request, 'edit_profile_student_page.html', {"MEDIA_URL":MEDIA_URL,"csrf_token": csrf_token , "error_edit" : True})
				
				"""----------User Succesfully Edited.---------------"""
				return HttpResponse(f'''<body><script>Details are successfully Edited.</script><meta http-equiv="refresh" content='0; url="/profile/"'/></body>''')

			if extract_user__user_signup_database.user_category == "TEACHER":
				input_data = request.POST
				
				no_error = True

				edit_full_name = input_data.get("edit_name", "").strip().lower().split()

				try:
					edit_first_name, edit_last_name = edit_full_name[0], edit_full_name[1]
					first_name_check = validation_check.nameCheck(edit_first_name)
					last_name_check = validation_check.nameCheck(edit_last_name)
				except:
					no_error = False

				edit_contact, edit_r_number = input_data.get("edit_contact", "0").strip(), input_data.get("edit_r_number", "0").strip()
				contact_check = validation_check.contactCheck(edit_contact)
				r_number_check = validation_check.rCheck(edit_r_number)


				edit_school_name = input_data.get("edit_school", "").strip()
				school_name_check = validation_check.schoolNameCheck(edit_school_name)

				if request.FILES:
					image_file = request.FILES.get("imagefile",None)
				else:
					image_file = None
				image_files_check = True
				if image_file:
					# lecture files are not compulsory.
					if len(image_file.name.strip()) > 100 or len(image_file.name.strip()) < 6:
						image_files_check = False
					reverse_file_name = image_file.name.strip()[::-1]
					file_extension = ""
					for char in reverse_file_name:
						file_extension += char
						if char == ".":
							break
					file_extension = file_extension[::-1]
					if not (file_extension in ALLOWED_IMAGE_FILE_TYPE):
						image_files_check = False

				if not (no_error and first_name_check and last_name_check  and contact_check and r_number_check and school_name_check and image_files_check):
				# handling tempered data.
				# The incoming data was corrupted (maybe using burpsuite.) (This is because, all the above validations were done at frontend, but still the value arent valid values.)
					return render(request, "edit_profile_teacher_page.html", {"MEDIA_URL":MEDIA_URL,"csrf_token": csrf_token , "error_edit" : True})

				"""----------Now all the input values are valid.---------------"""

				# data formatting.
				edit_first_name = edit_first_name[0].upper() + edit_first_name[1:]
				edit_last_name = edit_last_name[0].upper() + edit_last_name[1:]
				
				try:
					extract_user__user_signup_database.first_name = edit_first_name
					extract_user__user_signup_database.last_name = edit_last_name
					extract_user__user_signup_database.user_contact = edit_contact 
					extract_user__user_signup_database.user_r_number = edit_r_number
					extract_user__user_signup_database.school_name = edit_school_name
					extract_user__user_signup_database.save()

					extract_user__user_profile_database.user_signup_db_mapping = extract_user__user_signup_database
					extract_user__user_profile_database.user_profile_photo = image_file
					extract_user__user_profile_database.edit_once = True
					extract_user__user_profile_database.save()
					
				except:
					"""----------Some error while setting.---------------"""
					extract_user__user_profile_database.edit_once = False
					extract_user__user_profile_database.save()
					return render(request, 'edit_profile_teacher_page.html', {"csrf_token": csrf_token , "error_edit" : True})
			
				"""----------User Succesfully Edited.---------------"""
				return HttpResponse(f'''<body><script>Details are successfully Edited.</script><meta http-equiv="refresh" content='0; url="/profile/"'/></body>''')
		else:
			return render(request, "edit_page_not_allowed.html", {"MEDIA_URL":MEDIA_URL,"user_category":extract_user__user_signup_database.user_category, "preview_user": extract_user__user_signup_database, "preview_profile": extract_user__user_profile_database})
	else:
		# session is inactive.
		return HttpResponse(f'''<body><meta http-equiv="refresh" content='0; url="/login/"'/></body>''')
