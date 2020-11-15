from django.shortcuts import render,redirect
from django.contrib import auth
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Count
from datetime import datetime
from application.models import academy,student,teacher,device,device_apply,device_apply_record,device_broken,major
from application.models import classroom_apply,classroom,curriculum,classroom_apply_record,EmailVerifyRecord
from application.utils.email_send import send_register_email, send_reset_password_email
from django.utils import timezone

#首页，返回登录页面
def MIS_login(request):
	academies = []
	majors = []
	all_aca = academy.objects.all()
	for aca in all_aca:
		academies.append(aca.academy_name)
	all_maj = major.objects.all()
	for maj in all_maj:
		majors.append(maj.major_name)
	return render(request,'login.html', {'academies':academies, 'majors':majors})

def login(request):
	username = request.POST.get("username")	#获取账号
	password = request.POST.get("password")	#获取密码
	#检查账号是否存在，若存在密码是否正确，若不存在该账号或密码错误，则user为None
	user = auth.authenticate(username=username,password=password)
	if user is None:
		return JsonResponse({
			'status' : 'error',
			'code' : '400',
			'message' : '账号或密码错误'
		})
	
	#若账号存在且密码正确，则正常登录
	auth.login(request,user)
	return JsonResponse({
		'status' : 'success',
		'code' : '200',
		'message' : '登录成功'
	})

#登出函数
def logout(request):
	auth.logout(request)
	return redirect('/')

#返回首页
def homepage(request):
	#检查用户是否已登录
	#若没登录，重定向到登录页面
	#若已登录，判别用户身份，返回相应的首页
	if request.user.is_authenticated:
		if request.user.is_superuser:
			#返回管理员首页
			return render(request,'work/index.html')
		else:
			#返回用户首页
			context = {}
			user_info = {}
			user = request.user
			user_info['email'] = user.email
			user_info['account'] = user.username
			try:
				student= user.student
				user_info['is_stu'] = '学号'
				user_info['name']= student.student_name
				user_info['phone'] = student.phone
				user_info['academy'] = student.academy.academy_name
				user_info['major'] = student.major.major_name
				context['user_info'] = user_info 
			except:
				teacher = user.teacher
				user_info['is_stu'] = '工号'
				user_info['name'] = teacher.student_name
				user_info['phone'] = teacher.phone
				user_info['academy'] = teacher.academy.academy_name
				context['user_info'] = user_info
			return render(request,'user/index.html',context)
	else:
		return redirect('/')

def signup(request):
	# register_form = RegisterForm(request.POST)
	# if register_form.is_valid():
		username = request.POST.get("username", None)
		if(User.objects.filter(username=username)):
			return JsonResponse({
				'status' : 'error',
				'code' : '400',
				'message' : '账号已被注册',
				'username' : username,
			})
		password = request.POST.get("password", None)
		email = request.POST.get("email", None)
		phone = request.POST.get("phone", None)
		user_type = int(request.POST.get("type", None))
		maj = request.POST.get("major", None)
		aca = request.POST.get("academy", None)
		if maj:
			user_major = major.objects.get(major_name = maj)
		user_academy = academy.objects.get(academy_name = aca)
		name = request.POST.get("name", None)
		if(User.objects.filter(email=email)):
			return JsonResponse({
				'status' : 'error',
				'code' : '400',
				'message' : '邮箱已被注册',
				'username' : username,
				'password' : password,
				'email' : email,
			})
		user = User.objects.create_user(username = username, password = password, email = email)
		user.is_active = False # 设置为未激活状态
		user.save()
		if user_type == 0:
			s = student(user = user, student_name = name, academy = user_academy, major = user_major, phone = phone, status = False)
			s.save()
		elif user_type == 1:
			t = teacher(user = user, teacher_name = name, academy = user_academy, phone = phone, status = False)
			t.save()
		send_register_email(email, "register") # 调用发送邮件
		return JsonResponse({
			'status' : 'success',
			'code' : '200',
			'message' : '注册并激活成功',
			'username' : username,
			'password' : password,
			'email' : email,
		})
	
def active(request, active_code):
	# 如果保存的随机码中有刚才生成的那个，就说明成功验证
	all_records = EmailVerifyRecord.objects.filter(code = active_code)
	if all_records:
		for record in all_records:
			email = record.email
			user = User.objects.get(email = email)
			try:
				s = student.objects.get(user = user)
				s.status = True
				s.save()
			except:
				t = teacher.objects.get(user = user)
				t.status = True
				t.save()
			user.is_active = True
			user.save()
		all_records.delete()
	else:
		return redirect("/")
	return redirect("/")

def reset_password(request):
	# register_form = RegisterForm(request.POST)
	# if register_form.is_valid():
		username = request.POST.get("username", None)
		new_password = request.POST.get("password", None)
		email = request.POST.get("email", None)
		users = User.objects.filter(email=email, username=username)
		if users :
			for user in users:
				user.password = make_password(new_password)
				user.is_active = False # 设置为未激活状态
				user.save()
				send_reset_password_email(email, "reset_password") # 调用发送邮件
			return JsonResponse({
				'status' : 'success',
				'code' : '200',
				'message' : '账号已冻结，请查收邮件确认重置密码',
				'username' : username,
				# 'password' : new_password,
				'email' : email,
			})
		else:
			return JsonResponse({
				'status' : 'error',
				'code' : '400',
				'message' : '用户不存在，请重新输入',
				'username' : username,
				# 'password' : new_password,
				'email' : email,
			})

def confirm_reset(request, active_code):
	all_records = EmailVerifyRecord.objects.filter(code = active_code)
	if all_records:
		for record in all_records:
			user = User.objects.get(email=record.email)
			user.is_active = True
			user.save()
		context = {
			'status' : 'success',
			'code' : '200',
			'message' : '密码已重置，请重新登录',
		}
	else:
		context = {
			'status' : 'error',		
			'code' : '400',
			'message' : '信息有误，请重新找回密码',
		}
	return render(request, 'login.html', context)
#返回管理员首页的欢迎页面
def home(request):
	return render(request,'work/home.html')

#返回学生信息列表页面
def student_list(request):
	departments = academy.objects.all()
	majors = major.objects.all()
	return render(request,'work/student-list.html',{'departments':departments,'majors':majors})

def add_student(request):
	netid = request.GET.get('netid')
	name = request.GET.get('name')
	email = request.GET.get('email')
	phone = request.GET.get('phone')
	password = request.GET.get('password')
	academy_id = int(request.GET.get('academy'))
	major_id = int(request.GET.get('major'))

	try:
		m = major.objects.get(pk=major_id)
		d = academy.objects.get(pk=academy_id)
		if m.college.pk != d.pk:
			raise Exception()
		u = User.objects.create_user(username=netid,password=password,email=email)

		stu = student()
		stu.user = u
		stu.academy = d
		stu.major = m
		stu.student_name = name
		stu.phone = phone
		u.save()
		stu.save()

		return JsonResponse({
			'status' : 'success',
			'code' : '200',
			'message' : '添加成功'
		})
	except:
		return JsonResponse({
			'status' : 'error',
			'code' : '400',
			'message' : '添加失败'
		})

#返回学生信息
def student_info(request):
	pageSize = int(request.GET.get('pageSize'))		#获取每页的大小
	pageIndex = int(request.GET.get('pageIndex'))	#获取页码
	select_type = request.GET.get('select_type')	#获取选择类型
	condition = request.GET.get('condition')		#获取选择条件

	try:
		#根据选择类型和条件获取相应的信息
		if select_type == 'all':
			#筛选出全部学生信息记录
			student_infos = student.objects.filter()
		elif select_type == 'netid':
			#筛选出指定netid的学生信息记录
			u = User.objects.get(username = condition)
			student_infos = student.objects.filter(user = u)
		elif select_type == 'department':
			#筛选出指定学院的所有学生信息记录
			department = academy.objects.get(academy_name = condition)
			student_infos = student.objects.filter(academy = department)
		else:
			#筛选出指定专业的所有学生信息记录
			m = major.objects.get(major_name = condition)
			student_infos = student.objects.filter(major = m)

		student_infos_count = student_infos.count()	#符合条件的学生记录总数
		student_infos = student_infos[pageSize*(pageIndex-1):pageSize*pageIndex]	#指定页码数的学生信息记录	

		students = []
		for student_info in student_infos:
			context = {'check':''}
			context['netid'] = student_info.user.username	#学生账号
			context['name'] = student_info.student_name		#学生姓名
			context['department'] = student_info.academy.academy_name	#所属学院名称
			context['major'] = student_info.major.major_name			#所属专业名称
			context['email'] = student_info.user.email					#注册邮箱
			context['status'] = '已启用' if student_info.status else '已停用'	#账号状态
			students.append(context)
		return JsonResponse({
			'total' : student_infos_count,
			'rows' : students,
			'status' : 'success',
			'code' : '200',
			'message' : '请求成功'
		})
	except:
		return JsonResponse({
			'total':0,
			'rows' : [],
			'status' : 'error',
			'code' : '400',
			'message' : '参数出错'
		})

#返回教师信息页面
def teacher_list(request):
	departments = academy.objects.all()
	return render(request,'work/teacher-list.html',{'departments':departments})

def add_teacher(request):
	netid = request.GET.get('netid')
	name = request.GET.get('name')
	email = request.GET.get('email')
	phone = request.GET.get('phone')
	password = request.GET.get('password')
	academy_id = int(request.GET.get('academy'))

	try:
		d = academy.objects.get(pk=academy_id)
		u = User.objects.create_user(username=netid,password=password,email=email)

		tea = teacher()
		tea.user = u
		tea.academy = d
		tea.teacher_name = name
		tea.phone = phone
		u.save()
		tea.save()

		return JsonResponse({
			'status' : 'success',
			'code' : '200',
			'message' : '添加成功'
		})
	except:
		return JsonResponse({
			'status' : 'error',
			'code' : '400',
			'message' : '添加失败'
		})

def teacher_info(request):
	try:
		pageSize = int(request.GET.get('pageSize'))		#获取每页的大小
		pageIndex = int(request.GET.get('pageIndex'))	#获取页码
		select_type = request.GET.get('select_type')	#获取选择类型
		condition = request.GET.get('condition')		#获取选择条件

		#根据选择类型和条件获取相应的信息
		if select_type == 'all':
			#获取全部老师信息
			teacher_infos = teacher.objects.filter()
		elif select_type == 'netid':
			#获取指定工号老师的信息
			u = User.objects.get(username=condition)
			teacher_infos = teacher.objects.filter(user=u)
		elif select_type == 'department':
			#获取指定学院的老师的信息
			department = academy.objects.get(academy_name=condition)
			teacher_infos = teacher.objects.filter(academy = department)

		teacher_infos_count = teacher_infos.count()		#符合条件的记录总数
		teacher_infos = teacher_infos[pageSize*(pageIndex-1):pageSize*pageIndex]	#指定页码的记录

		teachers = []
		for teacher_info in teacher_infos:
			context = {'check' : ''}
			context['netid'] = teacher_info.user.username	#工号
			context['name'] = teacher_info.teacher_name		#教师姓名
			context['department'] = teacher_info.academy.academy_name	#所属学院名称
			context['email'] = teacher_info.user.email					#邮箱
			context['status'] = '已启用' if teacher_info.status else '已停用'	#账号状态
			teachers.append(context)
		return JsonResponse({
			'total' : teacher_infos_count,
			'rows' : teachers,
			'status' : 'success',
			'code' : '200',
			'message' : '请求成功'	
		})
	except:
		return JsonResponse({
			'total':0,
			'rows' : [],
			'status' : 'error',
			'code' : '400',
			'message' : '权限不足'
		})

#***停用用户
def suspend(request,netid):
	user = User.objects.get(username=netid)
	try:
		stu = user.student
		stu.status = False
		stu.save()
	except:
		tutor = user.teacher
		tutor.status = False
		tutor.save()

	return JsonResponse({
		'status' : 'success',
		'code' : '200',
		'message' : '已停用该用户'
	})

#恢复用户
def recover(request,netid):
	user = User.objects.get(username=netid)
	try:
		stu = user.student
		stu.status = True
		stu.save()
	except:
		tutor = user.teacher
		tutor.status = True
		tutor.save()

	return JsonResponse({
		'status' : 'success',
		'code' : '200',
		'message' : '已恢复该用户'
	})

#***删除用户
def delete(request,netid):
	user = User.objects.get(username=netid)
	try:
		stu = user.student
		stu.delete()
	except:
		tutor = user.teacher
		tutor.delete()

	user.delete()
	return JsonResponse({
		'status' : 'success',
		'code' : '200',
		'message' : '成功删除该用户'
	})

#***修改用户信息
def modify(request,netid):

	user = User.objects.get(username=netid)
	name = request.GET.get('name')
	email = request.GET.get('email')

	try:
		stu = user.student
		stu.student_name = name
		stu.save()
	except:
		tutor = user.teacher
		tutor.teacher_name = name
		tutor.save()

	user.email = email
	user.save()

	return JsonResponse({
		'status' : 'success',
		'code' : '200',
		'message' : '信息修改成功',
		'name' : name,
		'email' : email
	})

#返回设备信息列表页面
def device_list(request):
	return render(request,'work/device-list.html')

#返回符合条件的设备信息
def device_info(request):
	
	pageSize = int(request.GET.get('pageSize',None))	#获取每页大小
	pageIndex = int(request.GET.get('pageIndex',None))	#获取页码
	select_type = request.GET.get('select_type',None)	#获取选择类型
	status = int(request.GET.get('status',None))		#获取选择的设备状态参数

	if select_type == 'all':
		if status == 2:
			#检索出所有设备信息
			device_infos = device.objects.all()
		elif status == 1:
			#检索出所有可用的设备信息
			device_infos = device.objects.filter(status=True)
		else:
			#检索出所有不可用的设备信息
			device_infos = device.objects.filter(status=False)
	elif select_type == 'id':
		#检索出指定设备编号的设备信息
		id = request.GET.get('id')
		if status == 2:
			device_infos = device.objects.filter(pk=id)
		elif status == 1:
			device_infos = device.objects.filter(pk=id,status=True)
		else:
			device_infos = device.objects.filter(pk=id,status=False)
	elif select_type == 'name':
		#检索出指定设备名称的设备信息
		name = request.GET.get('name')
		if status == 2:
			device_infos = device.objects.filter(device_name=name)
		elif status == 1:
			device_infos = device.objects.filter(device_name=name,status=True)
		else:
			device_infos = device.objects.filter(device_name=name,status=False)
	else:
		#检索出指定设备类型的设备信息
		type = int(request.GET.get('type'))
		if status == 2:
			device_infos = device.objects.filter(device_type=type)
		elif status == 1:
			device_infos = device.objects.filter(device_type=type,status=True)
		else:
			device_infos = device.objects.filter(device_type=type,status=False)

	device_infos_count = device_infos.count()	#符合条件的设备数量
	device_infos = device_infos[pageSize*(pageIndex-1):pageSize*pageIndex]	#指定也页码的设备记录
		
	devices = []
	maps = {0:"多媒体",1:"桌椅",2:"其他"}

	for device_info in device_infos:
		context = {'check' : ''}
		context['device_id'] = device_info.pk	#设备编号
		context['device_type'] = maps[device_info.device_type]	#设备类型
		context['device_name'] = device_info.device_name	#设备名称
		context['status'] = '可用' if device_info.status else '不可用'	#设备状态
		context['location'] = device_info.storage_location	#存储位置
		context['netid'] = device_info.responsible_staff.username	#负责人工号
		context['time'] = device_info.last_check_time	#上次检修时间
		devices.append(context)

	return JsonResponse({
		'total' : device_infos_count,
		'rows' : devices,
		'status' : 'success',
		'code' : '200',
		'message' : '请求成功'	
	})

def add_device(request):
	type = int(request.GET.get('type'))	#获取设备类型
	name = request.GET.get('name')		#获取设备名称
	location = request.GET.get('location')	#获取设备存储地点
	stable = request.GET.get('stable')	#获取设备移动属性

	new_device = device()
	new_device.device_type = type
	new_device.device_name = name
	new_device.responsible_staff = request.user
	new_device.storage_location = location
	new_device.last_check_time = datetime.now()
	new_device.is_stable = False if stable == '1' else True
	new_device.save()

	return JsonResponse({
		'status' : 'success',
		'code' : '200',
		'message' : '添加设备成功'
	})

#***删除设备
def delete_device(request):
	items = request.GET.getlist('items')
	for item in items:
		device_info = device.objects.get(pk=int(item))
		device_info.delete()
	return JsonResponse({
		'status' : 'success',
		'code' : '200',
		'message' : '删除设备记录成功'
  	})

def Device_apply(request):
	return render(request,'work/device_apply.html')

def help1(request):
	infos = device_apply.objects.filter(apply_status=0,use_date__lt=datetime.now().date())
	for info in infos:
		info.pass_time = datetime.now()
		info.apply_head = request.user
		info.refuse_reason = '来不及审核'
		info.apply_status = 2
		info.save()

def device_apply_info(request):
	
	pageSize = int(request.GET.get('pageSize'))		#获取每页大小
	pageIndex = int(request.GET.get('pageIndex'))	#获取页码
	select_type = request.GET.get('select_type')	#获取选择类型
	condition = request.GET.get('condition')		#获取选择条件

	help1(request)

	if select_type == 'all':
		#获取所有的待审核申请单
		infos = device_apply.objects.filter(apply_status=0)
	else:
		#获取指定申请者的全部待审核申请单
		user = User.objects.get(username=condition)
		infos = device_apply.objects.filter(applicant=user,apply_status=0)

	infos_count = infos.count()		#符合条件的待审核申请单的数量
	infos = infos[pageSize*(pageIndex-1):pageSize*pageIndex]	#指定页码的申请单
		
	applys = []
	maps = {0:"多媒体",1:"桌椅",2:"其他"}

	for info in infos:
		context = {'check' : ''}
		context['apply_id'] = info.pk
		context['netid'] = info.applicant.username
		try:
			context['name'] = info.applicant.student.student_name
		except:
			context['name'] = info.applicant.teacher.teacher_name
		context['device_type'] = maps[info.device_type]
		context['device_name'] = info.device_name
		context['device_number'] = info.apply_quatity
		context['date'] = info.use_date
		context['location'] = info.classroom.classroom_id
		context['start_section'] = info.apply_section_begin
		context['end_section'] = info.apply_section_end
		context['reason'] = info.apply_reason
		context['operate'] = info.pk
		applys.append(context)
	return JsonResponse({
		'total' : infos_count,
		'rows' : applys,
		'status' : 'success',
		'code' : '200',
		'message' : '请求成功'	
	})

def detail(request):
	apply_id = int(request.GET.get('apply_id'))	#获取申请单号
	apply_form = device_apply.objects.get(pk=apply_id)
	return render(request,'work/detail.html',{'apply_id' : apply_id,'number':apply_form.apply_quatity})	

def help():
	infos = device_apply_record.objects.filter(use_date__lt=datetime.now().date())
	for info in infos:
		info.delete()

def detail_info(request,apply_id):
	#获取指定的申请单
	apply = device_apply.objects.get(pk=int(apply_id))

	#获取选择条件
	use_date = apply.use_date
	start_section = apply.apply_section_begin
	end_section = apply.apply_section_end
	type = apply.device_type
	name = apply.device_name

	#初步符合条件的设备
	device_infos = device.objects.filter(status=True,is_stable=False,device_type=type,device_name=name)
	help()

	devices = []
	maps = {0:"多媒体",1:"桌椅",2:"其他"}

	for device_info in device_infos:
		device_records = device_apply_record.objects.filter(use_date=use_date,device=device_info)
		flag = True
		for record in device_records:
			if not (end_section < record.section_begin or start_section > record.section_end):
				flag = False
		if flag:
			context = {'check' : ''}
			context['device_id'] = device_info.pk
			context['device_type'] = maps[device_info.device_type]
			context['device_name'] = device_info.device_name
			context['status'] = '可用' if device_info.status else '不可用'
			context['location'] = device_info.storage_location
			context['time'] = device_info.last_check_time
			devices.append(context)

	return JsonResponse({
			'total' : len(devices),
			'rows' : devices,
			'status' : 'success',
			'code' : '200',
			'message' : '请求成功'	
		})

def reject_apply(request):
	apply_id = request.GET.get('apply_id')	#获取相应的申请单号
	reject_reason = request.GET.get('reason')

	apply = device_apply.objects.get(pk=int(apply_id))
	apply.apply_status = 2
	apply.pass_time = datetime.now()
	apply.apply_head = request.user
	apply.refuse_reason = reject_reason

	apply.save()
	return JsonResponse({
		'status' : 'success',
		'code' : '200',
		'message' : '拒绝申请成功'
	})

def agree_apply(request):
	apply_id = request.GET.get('apply_id')
	device_ids = request.GET.getlist('device_ids')

	apply = device_apply.objects.get(pk=apply_id)
	apply.apply_status = 1
	apply.pass_time = datetime.now()
	apply.apply_head = request.user
	apply.save()

	for device_id in device_ids:
		record = device_apply_record()
		record.apply = apply
		record.device = device.objects.get(pk=int(device_id))
		record.use_date = apply.use_date
		record.section_begin = apply.apply_section_begin
		record.section_end = apply.apply_section_end
		record.save()

	return JsonResponse({
		'status' : 'success',
		'code' : '200',
		'message' : '同意申请成功!'
	})

def Device_apply_record(request):
	return render(request,'work/device_apply_record.html')

def device_apply_record_info(request):
	
	pageSize = int(request.GET.get('pageSize'))
	pageIndex = int(request.GET.get('pageIndex'))
	select_type = request.GET.get('select_type')
	condition = request.GET.get('condition')

	if select_type == 'all':
		infos = device_apply.objects.filter(apply_status__in=[1,2])
	elif select_type == "netid":
		u = User.objects.get(username=condition)
		infos = device_apply.objects.filter(applicant=u,apply_status__in=[1,2])
	else:
		u = User.objects.get(username=condition)
		infos = device_apply.objects.filter(apply_head=u,apply_status__in=[1,2])

	infos_count = infos.count()
	infos = infos[pageSize*(pageIndex-1):pageSize*pageIndex]

	applys = []
	for info in infos:
		context = {'check' : ''}
		context['apply_id'] = info.pk
		context['netid'] = info.applicant.username	
		try:
			context['name'] =info.applicant.student.student_name
		except:
			context['name'] = info.applicant.teacher.teacher_name
		context['apply_date'] = info.apply_time
		context['pass_user_id'] = info.apply_head.username
		context['pass_user_name'] = info.apply_head.staff.staff_name
		context['pass_status'] = '通过'  if info.apply_status == 1 else '不通过'
		context['pass_date'] = info.pass_time
		applys.append(context)

	return JsonResponse({
		'total' : infos_count,
		'rows' : applys,
		'status' : 'success',
		'code' : '200',
		'message' : '请求成功'	
	})

def Device_broken(request):	
	return render(request,'work/device_broken.html')

def device_broken_info(request,record_index=-1):
	pageSize = int(request.GET.get('pageSize'))
	pageIndex = int(request.GET.get('pageIndex'))
	select_type = request.GET.get('select_type')
	condition = request.GET.get('condition')
	if(request.GET.get('record_id')!=None):
		record_index=int(request.GET.get('record_id'))

	# 返回已完成维修信息
	if record_index!=-1:
		applys=[]
		infos=device_broken.objects.filter(pk=record_index);
		infos_count = infos.count()
		for info in infos:
			context={'check' : ''}
			context['device_id'] = info.device.pk
			context['pass_time'] = info.pass_time;
			context['pass_user'] = str(info.pass_user);
			applys.append(context)
		return JsonResponse({
			'total' : infos_count,
			'rows' : applys,
			'status' : 'success',
			'code' : '200',
			'message' : '请求成功'
		})


	if select_type == 'all':
		infos = device_broken.objects.filter()
	elif select_type == "netid":
		u = User.objects.get(username=condition)
		infos = device_broken.objects.filter(applicant=u)

	infos_count = infos.count()
	infos = infos[pageSize*(pageIndex-1):pageSize*pageIndex]
		
	applys = []
	maps = {0:"多媒体",1:"桌椅",2:"其他"}

	for info in infos:
		context = {'check' : ''}
		context['netid'] = info.applicant.username
		try:
			context['name'] = info.applicant.student.student_name
		except:
			context['name'] = info.applicant.teacher.teacher_name
		context['device_id'] = info.device.pk
		context['device_type'] = maps[info.device.device_type]
		context['device_name'] = info.device.device_name
		context['detail'] = info.detail
		context['date'] = info.submit_time
		context['status_operate']={'status':info.status,'operate':info.pk}
		context['operate'] = info.pk
		applys.append(context)

	return JsonResponse({
		'total' : infos_count,
		'rows' : applys,
		'status' : 'success',
		'code' : '200',
		'message' : '请求成功'	
	})

def deal_broken(request):
	id = request.GET.get('id')
	record = device_broken.objects.get(pk=int(id))
	record.device.status = True
	record.device.save()

	record.pass_time = datetime.now()
	record.status = True
	record.pass_user = request.user
	record.save()

	return JsonResponse({
		'status' : 'success',
		'code' : '200',
		'message' : '处理成功'
	})

def submit(request):
	device_id = request.GET.get('device_id')
	detail = request.GET.get('detail')
	
	n = device_broken()
	n.applicant = request.user
	n.device = device.objects.get(pk=int(device_id))
	n.detail = detail
	n.save()
	
	n.device.status = False
	n.device.save()
	
	return JsonResponse({
		'status' : 'success',
		'code' : '200',
		'message' : '提交成功',
		})

def get_device_apply_info(request):
	infos = device_apply.objects.filter(applicant=request.user)
	applys = []
	for info in infos:
		apply = list()
		apply.append(info.id)
		apply.append(info.device_type)
		apply.append(info.device_name)
		apply.append(info.apply_quatity)
		apply.append(info.classroom.classroom_id)
		apply.append(info.use_date)
		apply.append(info.apply_section_begin)
		apply.append(info.apply_section_end)
		apply.append(info.apply_reason)
		apply.append(apply_status)
		applys.append(apply)

	return JsonResponse({
		'status' : 'success',
		'code' : '200',
		'message' : '获取数据成功',
		'info' : applys
	})

def submit_device_apply(request):
	device_type = request.GET.get('type')
	device_name = request.GET.get('name')
	number = request.GET.get('number')
	reason = request.GET.get('reason')
	classroom_id = request.GET.get('classroom')
	dates = request.GET.get('date').split('-')
	start = request.GET.get('start_section')
	end = request.GET.get('end_section')

	apply = device_apply()
	apply.applicant = request.user
	apply.device_type = int(device_type)
	apply.device_name = device_name
	apply.use_date = datetime(year=int(dates[0]),month=int(dates[1]),day=int(dates[2])).date()
	apply.apply_quatity = int(number)
	apply.classroom = classroom.objects.get(classroom_id=classroom_id)
	apply.apply_section_begin = int(start)
	apply.apply_section_end = int(end)
	apply.apply_reason = reason
	apply.save()

	return JsonResponse({
		'status' : 'success',
		'code' : '200',
		'message' : '申请提交成功'
	})

def apply_detail(request):
	apply_id = int(request.GET.get('apply_id'))
	apply = device_apply.objects.get(pk=apply_id)
	maps = {0:"多媒体",1:"桌椅",2:"其他"}
	try:
		apply.name = apply.applicant.student.student_name
	except:
		apply.name = apply.applicant.teacher.teacher_name
	apply.type = maps[apply.device_type]
	return render(request,'work/apply_detail.html',{'apply':apply})


def classroom_apply_1(request):
	if request.user.is_authenticated and request.user.is_superuser:
		return render(request,'work/classroom-apply-1.html')
	else:
		return redirect('/')

def apply_classroom_list_1(request): #展示待初审的申请表单
	if request.user.is_authenticated and request.user.is_superuser:
		search_word = request.GET.get('search_word')
		search_type = request.GET.get('search_type')
		pageSize = int(request.GET.get('pageSize'))
		pageIndex = int(request.GET.get('pageIndex'))

		applies = classroom_apply.objects.filter(apply_status = 0)
		if search_type == 'apply_id':
			applies = applies.filter(id = int(search_word))
		elif search_type == 'applicant':
			u = User.objects.get(username=search_word)
			applies = applies.filter(applicant = u)
		
		apply_list = []
		apply_list_count = applies.count()
		applies = applies[pageSize*(pageIndex-1):pageSize*pageIndex]

		for apply in applies:
			content = {'check' : ''}
			content['classroom_apply_id'] = apply.id
			try:
				content['applicant_id'] = apply.applicant.student.student_name
			except:
				content['applicant_id'] = apply.applicant.teacher.teacher_name
			content['responsible_teacher'] = apply.responsible_teacher.teacher_name
			content['apply_time'] = apply.apply_time
			content['apply_date'] = apply.use_date
			content['apply_section_begin'] = apply.apply_section_begin
			content['apply_section_end'] = apply.apply_section_end
			content['apply_size'] = apply.apply_size
			apply_list.append(content)
		return JsonResponse({
			'rows' : apply_list,
			'total' : apply_list_count,
			'status' : 'success',
			'code' : '200',
			'message' : '查询成功',
		})
	else:
		return JsonResponse({
			'status' : 'error',
			'code' : '400',
			'message' : '权限不足',
		})

def classroom_apply_2(request):
	if request.user.is_authenticated and request.user.is_superuser:
		return render(request,'work/classroom-apply-2.html',{})
	else:
		return redirect('/')

def apply_classroom_list_2(request): #展示待复审的申请表单
	if request.user.is_authenticated and request.user.is_superuser:
		search_word = request.GET.get('search_word')
		search_type = request.GET.get('search_type')
		pageSize = int(request.GET.get('pageSize'))
		pageIndex = int(request.GET.get('pageIndex'))

		applies = classroom_apply.objects.filter(apply_status = 1)
		if search_type == 'apply_id':
			applies = applies.filter(id = int(search_word))
		elif search_type == 'applicant':
			u = User.objects.get(username=search_word)
			applies = applies.filter(applicant = u)
		elif search_type == 'apply_head_1':
			u = User.objects.get(username=search_word)
			applies = applies.filter(apply_head_1 = u)

		apply_list = []
		apply_list_count = applies.count()
		applies = applies[pageSize*(pageIndex-1):pageSize*pageIndex]
		maps = {0:"普通课室",1:"多媒体课室",2:"多媒体录播课室"}

		for apply in applies:
			content = {}
			content['classroom_apply_id'] = apply.id
			try:
				content['applicant_id'] = apply.applicant.student.student_name
			except:
				content['applicant_id'] = apply.applicant.teacher.teacher_name
			content['responsible_teacher'] = apply.responsible_teacher.teacher_name
			content['apply_time'] = apply.apply_time
			content['apply_date'] = apply.use_date
			content['apply_section_begin'] = apply.apply_section_begin
			content['apply_section_end'] = apply.apply_section_end
			content['apply_size'] = apply.apply_size
			content['apply_category'] = maps[apply.apply_category]
			# content['apply_head_1'] = apply.apply_head_1.staff.staff_name
			content['apply_head_1'] = apply.apply_head_1.username
			content['pass_time_1'] = apply.pass_time_1
			apply_list.append(content)
		return JsonResponse({
			'rows' : apply_list,
			'total' : apply_list_count,
			'status' : 'success',
			'code' : '200',
			'message' : '查询成功',
		})
	else:
		return JsonResponse({
			'status' : 'error',
			'code' : '400',
			'message' : '权限不足',
		})

def classroom_apply_reason(request, classroom_apply_id):
	if request.user.is_authenticated and request.user.is_superuser:
		reason = classroom_apply.objects.get(id = int(classroom_apply_id)).apply_reason
		return JsonResponse({
			'status' : 'success',
			'code' : '200',
			'message' : '请求成功',
			'classroom_apply_id' : classroom_apply_id,
			'reason' : reason,
		})
	else:
		return JsonResponse({
			'status' : 'error',
			'code' : '400',
			'message' : '权限不足',
		})

def pass_classroom_apply_2(request, classroom_apply_id):
	if request.user.is_authenticated and request.user.is_superuser:
		apply = classroom_apply.objects.get(id = int(classroom_apply_id))
		apply.apply_head_2 = request.user
		apply.pass_time_2 = timezone.datetime.now()
		apply.apply_status = 2
		record = classroom_apply_record(apply=apply, classroom=apply.classroom, use_date = apply.use_date, apply_section_begin = apply.apply_section_begin,apply_section_end = apply.apply_section_end)
		record.save()
		apply.save()
		return JsonResponse({
			'classroom_apply_id' : classroom_apply_id,
			'status' : 'success',
			'code' : '200',
			'message' : '复审通过',
			'apply_head_2' : request.user.username,
			'apply_pass_time_2' : apply.pass_time_2,
		})
	else:
		return JsonResponse({
			'status' : 'error',
			'code' : '400',
			'message' : '权限不足',
		})

def classroom_list(request):
	if request.user.is_authenticated and request.user.is_superuser:
		return render(request,'work/classroom-list.html',{})
	else:
		return redirect('/')

def classroom_info(request):
	if request.user.is_authenticated and request.user.is_superuser:
		pageSize = int(request.GET.get('pageSize',None))
		pageIndex = int(request.GET.get('pageIndex',None))
		build = request.GET.get('build', None)
		floor = request.GET.get('floor', None)
		size = request.GET.get('size', None)
		category = request.GET.get('category', None)
		classrooms = classroom.objects.all()
		if category:
			category = int(category)
			classrooms = classrooms.filter(category = category)
		if size:
			size = int(size)
			classrooms = classrooms.filter(size=size)	
		if build:
			classrooms = classrooms.filter(classroom_id__startswith = build)
		if floor:
			floor = floor + "0"
			classrooms = classrooms.filter(classroom_id__contains = floor)
		classrooms_count = classrooms.count()
		classrooms = classrooms[pageSize*(pageIndex-1) : pageSize*pageIndex]
		classroom_infos = []
		if classrooms:
			for _classroom in classrooms:
				content = {}
				content['classroom_id'] = _classroom.classroom_id
				content['status'] = '已启用' if _classroom.status else '已停用'
				content['size'] = _classroom.size
				if _classroom.category == 0:
					str_category = '普通课室'
				elif _classroom.category == 1:
					str_category = '多媒体课室'
				elif _classroom.category == 2:
					str_category = '多媒体录播课室'
				content['category'] = str_category
				classroom_infos.append(content)
		
		return JsonResponse({
			'status' : 'success',
			'code' : '200',
			'message' : '查询成功',
			'total' : classrooms_count,
			'rows' : classroom_infos,
		})
	else:
		return JsonResponse({
			'status' : 'error',
			'code' : '400',
			'message' : '权限不足',
		})

def add_classroom(request, classroom_id):
	if request.user.is_authenticated and request.user.is_superuser:
		classroom_size = request.GET.get('classroom_size')
		category = int(request.GET.get('classroom_category'))
		count = classroom.objects.filter(classroom_id = classroom_id).count()
		if count > 0:
			return JsonResponse({
				'status' : 'error',
				'code' : '500',
				'message' : '课室: ' + classroom_id + ' 已存在！',
			})
		else:
			c = classroom(classroom_id = classroom_id, size = int(classroom_size), category = category, status = False)
			c.save()
			if category == 0:
				category = '普通课室'
			elif category == 1:
				category = '多媒体课室'
			elif category == 2:
				category = '多媒体录播课室'
			return JsonResponse({
				'status' : 'success',
				'code' : '200',
				'message' : '课室: ' + classroom_id + ', 规模: ' + classroom_size + ', 类别: '+ category +' 已成功添加, 状态默认停用',
				'classroom_id' : classroom_id,
				'classroom_size' : classroom_size,
				'classroom_category' : category,
			})
	else:
		return JsonResponse({
			'status' : 'error',
			'code' : '400',
			'message' : '权限不足',
		}) 

def suspend_classroom(request, classroom_id):
	if request.user.is_authenticated and request.user.is_superuser:
		_classroom = classroom.objects.get(classroom_id = classroom_id)
		_classroom.status = False
		_classroom.save()
		return JsonResponse({
			'status' : 'success',
			'code' : '200',
			'message' : '课室已停用',
		})
	else:
		return JsonResponse({
			'status' : 'error',
			'code' : '400',
			'message' : '权限不足',
		})

def active_classroom(request, classroom_id):
	if request.user.is_authenticated and request.user.is_superuser:
		_classroom = classroom.objects.get(classroom_id = classroom_id)
		_classroom.status = True
		_classroom.save()
		return JsonResponse({
			'status' : 'success',
			'code' : '200',
			'message' : '课室状态已启用',
		})
	else:
		return JsonResponse({
			'status' : 'error',
			'code' : '400',
			'message' : '权限不足',
		})

def classroom_device(request, classroom_id):
	if request.user.is_authenticated and request.user.is_superuser:
		pageIndex = int(request.GET.get('pageIndex'))
		pageSize = int(request.GET.get('pageSize'))
		devices = device.objects.filter(storage_location = classroom_id, is_stable = True)
		device_list = []
		maps = {0:"多媒体",1:"桌椅",2:"其他"}
		device_list_count = devices.count()
		if devices:
			devices = devices.values_list('device_type', 'device_name').annotate(device_count = Count('id'))
			device_list_count = devices.count()
			devices = devices[pageSize*(pageIndex-1) : pageSize*pageIndex]
			for d in devices:
				content = {}
				content['device_type'] = maps[d[0]]
				content['device_name'] = d[1]
				content['device_count'] = d[2]
				device_list.append(content)
		
		return JsonResponse({
			'status' : 'success',
			'code' : '200',
			'message' :'查找成功',
			'total' : device_list_count,
			'rows' : device_list,
		})
	else:
		return JsonResponse({
			'status' : 'error',
			'code' : '400',
			'message' : '权限不足',
		})

def classroom_detail(request, classroom_id):
	if request.user.is_authenticated and request.user.is_superuser:
		data = []
		room = classroom.objects.get(classroom_id=classroom_id)
		#三个类别的数据
		today = timezone.datetime.today().date()
		later = today + timezone.timedelta(days = 14)
		weekday = today.weekday()
		applies = classroom_apply.objects.filter(classroom = room, apply_status__in = [1,2], use_date__gte = today, use_date__lte = later )
		for apply in applies:
			delta = (apply.use_date - today).days
			content = [apply.apply_section_begin, apply.apply_section_end, delta, apply.apply_status, apply.id]
			data.append(content)
		courses = curriculum.objects.filter(classroom = room)
		print(room)
		print(courses)
		for course in courses:
			delta = course.week_day -1 - weekday
			if delta < 0 :
				content = [course.section_begin, course.section_end, delta+7, 0, course.course_name]
				data.append(content)
				content = [course.section_begin, course.section_end, delta+14, 0, course.course_name]
				data.append(content)
			else:
				content = [course.section_begin, course.section_end, delta, 0, course.course_name]
				data.append(content)
				content = [course.section_begin, course.section_end, delta+7, 0, course.course_name]
				data.append(content)
		context = {}
		context['data'] = data

		return render(request,'work/timetable_echarts.html',context)
	else:
		return redirect('/')

def modify_classroom(request, classroom_id):
	if request.user.is_authenticated and request.user.is_superuser:
		new_id = request.GET.get('new_id')
		new_size = request.GET.get('size')
		new_category = request.GET.get('category')
		if classroom_id != new_id :
			if classroom.objects.get(classroom_id = new_id):
				return JsonResponse({
					'status' : 'error',
					'code' : '400',
					'message' : '新命名课室已存在！'
				})
		room = classroom.objects.get(classroom_id = classroom_id)
		room.classroom_id = new_id
		room.size = new_size
	
		if new_category:
			room.category = new_category
			room.save()

		if room.category == 0:
			str_category = '普通课室'
		elif room.category == 1:
			str_category = '多媒体课室'
		else :
			str_category = '多媒体录播课室'
		
		return JsonResponse({
			'status' : 'success',
			'code' : '200',
			'message' : '修改成功',
			'new_id' : new_id,
			'new_size' : new_size,
			'new_category' : str_category,
			})
		
	else:
		return JsonResponse({
			'status' : 'error',
			'code' : '400',
			'message' : '权限不足',
		})

def Classroom_apply_record(request):
	if request.user.is_authenticated and request.user.is_superuser:
		return render(request,'work/classroom-apply-record.html',{})
	else:
		return redirect('/')

def apply_classroom_record(request):
	if request.user.is_authenticated and request.user.is_superuser:
		search_type = int(request.GET.get('search_type'))
		pageSize = int(request.GET.get('pageSize'))
		pageIndex = int(request.GET.get('pageIndex'))

		if search_type < 3 :
			applies = classroom_apply.objects.filter(apply_status = search_type)
		elif search_type == 3:
			applies = classroom_apply.objects.filter(apply_status = 3)
		else:
			applies = classroom_apply.objects.all()

		list_count = applies.count()
		applies = applies[pageSize*(pageIndex-1) : pageSize*pageIndex]
		apply_list = []
		maps = {0:"普通课室",1:"多媒体课室",2:"多媒体录播课室"}

		for apply in applies:
			content = {'check' : ''}
			content['classroom_apply_id'] = apply.id
			try:
				content['applicant_id'] = apply.applicant.student.student_name
			except:
				content['applicant_id'] = apply.applicant.teacher.teacher_name	
			content['apply_time'] = apply.apply_time
			content['apply_category'] = maps[apply.apply_category]
			content['apply_date'] = apply.use_date
			content['apply_section_begin'] = apply.apply_section_begin
			content['apply_section_end'] = apply.apply_section_end
			content['apply_size'] = apply.apply_size
			if apply.apply_head_1 is not None:
				content['apply_head_1'] = apply.apply_head_1.staff.staff_name
				content['pass_time_1'] = apply.pass_time_1
			if apply.apply_head_2 is not None:
				content['apply_head_2'] = apply.apply_head_2.staff.staff_name
				content['pass_time_2'] = apply.pass_time_2

			if apply.apply_status == 0 :
				content['apply_status'] = '待初审'
			elif apply.apply_status == 1 :
				content['apply_status'] = '待复审'
			elif apply.apply_status == 2 :
				content['apply_status'] = '待使用'
			elif apply.apply_status == 3 :
				content['apply_status'] = '已拒绝'
			apply_list.append(content)
		
		return JsonResponse({
			'total' : list_count,
			'rows' : apply_list,
			'status' : 'success',
			'code' : '200',
			'message' : '请求成功',
		})
	else:
		return JsonResponse({
			'status' : 'error',
			'code' : '400',
			'message' : '权限不足',
		})



def delete_classroom(request, classroom_id):
	if request.user.is_authenticated and request.user.is_superuser:
		room = classroom.objects.get(classroom_id = classroom_id)
		room.device_apply_classroom.update(apply_status = 3, refuse_reason = "目标课室已失效")
		room.classroom_apply_classroom.update(apply_status = 3, refuse_reason = "目标课室已失效")
		room.delete()
		return JsonResponse({
			'status' : 'success',
			'code' : '200',
			'message' : '课室已删除',
		})
	else:
		return JsonResponse({
			'status' : 'error',
			'code' : '400',
			'message' : '权限不足',
		})


def refuse_classroom_apply(request, classroom_apply_id):
	if request.user.is_authenticated and request.user.is_superuser:
		apply = classroom_apply.objects.get(id = int(classroom_apply_id))
		reason = request.GET.get('refuse_reason')
		if apply.apply_status == 0:
			apply.apply_status = 3
			apply.apply_head_1 = request.user
			apply.pass_time_1 = datetime.now()
			apply.refuse_reason = reason
			apply.save()
		elif apply.apply_status == 1:
			apply.apply_status = 3
			apply.apply_head_2 = request.user
			apply.pass_time_2 = datetime.now()
			apply.refuse_reason = reason
			apply.save()
		return JsonResponse({
			'code' : '200',
			'status' : 'success',
			'message' : '已拒绝',
			'classroom_apply_id' : classroom_apply_id,
			'applicant' : request.user.username,
		})
	else:
		return JsonResponse({
			'status' : 'error',
			'code' : '400',
			'message' : '权限不足',
		})

def pass_classroom_apply_1(request, classroom_apply_id):
	if request.user.is_authenticated and request.user.is_superuser:
		classroom_id = request.GET.get('classroom_id')
		apply_id = classroom_apply_id
		apply = classroom_apply.objects.get(id = int(apply_id))
		apply.classroom = classroom.objects.get(classroom_id=classroom_id)
		apply.apply_head_1 = request.user
		apply.pass_time_1 = timezone.datetime.now()
		apply.apply_status = 1
		apply.save()
		return JsonResponse({
			'classroom_apply_id' : classroom_apply_id,
			'classroom_id' : classroom_id,
			'status' : 'success',
			'code' : '200',
			'message' : '初审通过',
			'apply_head_1' : request.user.username,
			'apply_pass_time_1' : apply.pass_time_1,
		})
	else:
		return JsonResponse({
			'status' : 'error',
			'code' : '400',
			'message' : '权限不足',
		})

def choose_available_classroom(request, classroom_apply_id):
	if request.user.is_authenticated and request.user.is_superuser:
		apply = classroom_apply.objects.get(id = int(classroom_apply_id))
		use_date = apply.use_date
		apply_size = apply.apply_size
		apply_section_begin = apply.apply_section_begin
		apply_section_end = apply.apply_section_end
		apply_category = apply.apply_category

		pageSize = int(request.GET.get('pageSize'))
		pageIndex = int(request.GET.get('pageIndex'))

		rooms = classroom.objects.filter(status=True,size=apply_size,category=apply_category)
		classroom_applies = classroom_apply.objects.filter(use_date=use_date,apply_status__in=[1,2])

		available_classrooms = []
		available_classrooms_count = 0
		maps = {0:"普通课室",1:"多媒体课室",2:"多媒体录播课室"}

		for room in rooms:
			flag = True
			for room_apply in classroom_applies:
				if room_apply.classroom.classroom_id == room.classroom_id and not (apply_section_end<room_apply.apply_section_begin \
					or apply_section_begin > room_apply.apply_section_end):
					flag = False
					break
			if flag:
				available_classrooms_count = available_classrooms_count + 1
				content = {"check" : ''}
				content['classroom_id'] = room.classroom_id
				content['classroom_size'] = room.size
				content['classroom_category'] = maps[room.category]
				available_classrooms.append(content)
			
		
		return JsonResponse({
			'status' : 'success',
			'code' : '200',
			'message' : '查询成功',
			'total' : available_classrooms_count,
			'rows' : available_classrooms[pageSize*(pageIndex-1) : pageSize*pageIndex],
		})	
	else:
		return JsonResponse({
			'status' : 'error',
			'code' : '400',
			'message' : '权限不足',
		})

# 首页用户待完成申请
def get_classroom_apply_info(request):
	user = request.user
	applies = classroom_apply.objects.filter(applicant = user, apply_status__in = [0,1,2])
	rows = []
	total = applies.count()
	if applies:
		for apply in applies:
			content = {}
			content['classroom_apply_id'] = apply.id
			content['use_date'] = apply.use_date
			content['section_begin'] = apply.apply_section_begin
			content['section_end'] = apply.apply_section_end
			content['apply_size'] = apply.apply_size
			content['apply_category'] = apply.apply_category
			content['apply_reason'] = apply.apply_reason
			content['apply_status'] = apply.apply_status
			if apply.classroom:
				content['classroom'] = apply.classroom.classroom_id
			else:
				content['classroom'] = '未分配'
			rows.append(content)
	return JsonResponse({
		'code' : '200',
		'status' : 'success',
		'total' : total,
		'rows' : rows,
	})

# 申请课室
def apply_classroom(request):
	date = request.POST.get('date', None)
	start_section = request.POST.get('start_section', None)
	end_section = request.POST.get('end_section', None)
	size = request.POST.get('size', None)
	category = request.POST.get('type', None)
	reason = request.POST.get('apply_reason', None)
	responsible_teacher = request.POST.get('responsible_teacher', None)
	teach = User.objects.get(username = responsible_teacher)
	date = date.split('-')
	day = timezone.datetime.today().date()
	day.replace(year = int(date[0]), month = int(date[1]), day = int(date[2]))
	r_teacher = teacher.objects.get(user = teach)
	size = int(size)
	category = int(category)
	start_section = int(start_section)
	end_section = int(end_section)
	apply = classroom_apply(applicant = request.user, use_date = day, apply_section_begin = start_section, apply_section_end = end_section, apply_reason = reason, apply_category = category, apply_size = size, responsible_teacher = r_teacher)
	apply.save()
	return JsonResponse({
		'code' : '200',
		'status' : 'success',
		'message' : '申请成功',
	})
	
	
def apply_classroom_page(request):
	name = request.user.username
	email = request.user.email
	context = {}
	user_info = {}
	academy_teachers = []
	user = request.user
	user_info['email'] = user.email
	try:
		student = user.student
		user_info['name'] = student.student_name
		user_info['phone'] = student.phone
		academy = student.academy
	except:
		apply_teacher = user.teacher
		user_info['name'] = apply_teacher.teacher_name
		user_info['phone'] = apply_teacher.phone
		academy = apply_teacher.academy
	teachers = teacher.objects.filter(academy = academy)
	for teach in teachers:
		t = {}
		t['teacher_name'] = teach.teacher_name
		t['teacher_account'] = teach.user.username
		academy_teachers.append(t)
	context['user_info'] = user_info
	context['academy_teachers'] = academy_teachers
	context['name'] = name
	context['email'] = email
	return render(request, 'user/application.html',context)




def multimedia_demand_submit(request):
	name = request.user.username
	email = request.user.email
	rooms = classroom.objects.all()
	try:
		member = request.user.student
		member.name = member.student_name
	except:
		member = request.user.teacher
		member.name = member.teacher_name
	return render(request,'user/multimedia_demand_submit.html',{'rooms':rooms,'member':member})

def repair_message_submit(request):
	name = request.user.username
	email = request.user.email
	try:
		member = request.user.student
		member.name = member.student_name
	except:
		member = request.user.teacher
		member.name = member.teacher_name
	return render(request,'user/repair_message_submit.html',{'member':member})

def device_record(request):
	name = request.user.username
	email = request.user.email
	try:
		member = request.user.student
		member.name = member.student_name
	except:
		member = request.user.teacher
		member.name = member.teacher_name
	return render(request,'user/device-record.html',{'member':member})

def get_device_apply_info(request):
	infos = device_apply.objects.filter(applicant=request.user)
	applys = []
	maps = {0:"多媒体",1:"桌椅",2:"其他"}
	for info in infos:
		apply = list()
		apply.append(info.id)
		apply.append(maps[info.device_type])
		apply.append(info.device_name)
		apply.append(info.apply_quatity)
		apply.append(info.classroom.classroom_id)
		apply.append(info.use_date)
		apply.append(info.apply_section_begin)
		apply.append(info.apply_section_end)
		apply.append(info.apply_reason)
		if info.apply_status == 0:
			apply.append('待审核')
		elif info.apply_status == 1:
			apply.append("已通过")
		else:
			apply.append("不通过")
		applys.append(apply)
	return JsonResponse({
		'status' : 'success',
		'code' : '200',
		'message' : '获取数据成功',
		'info' : applys
		})

def Application(request):
	name = request.user.username
	email = request.user.email
	try:
		member = request.user.student
		member.name = member.student_name
	except:
		member = request.user.teacher
		member.name = member.teacher_name
	return render(request,'user/application.html',{'member':member})

def search_classroom(request):
	name = request.user.username
	email = request.user.email
	date = request.GET.get('date', None)
	start_section = request.GET.get('start_section', None)
	end_section = request.GET.get('end_section', None)
	size = request.GET.get('size', None)
	category = request.GET.get('category', None)
	# pageSize = int(request.GET.get('pageSize', None))
	# pageIndex = int(request.GET.get('pageIndex', None))
	if date:
		dates = date.split('-')
		use_date = datetime(year=int(dates[0]),month=int(dates[1]),day=int(dates[2])).date()
		fulls = classroom_apply.objects.filter(use_date = use_date, apply_section_begin__lte = end_section, apply_section_end__gte = start_section)
		fulls = fulls.values('classroom').distinct()
		for full in fulls:
			rooms.exclude(classroom_id = full.classroom.classroom_id)
	
	rooms = classroom.objects.filter(status=True)
	if category:
		category = int(category)
		rooms = rooms.filter(category = category)
	if size:
		size = int(size)
		rooms = rooms.filter(size__gte = size)
	total = rooms.count()
	rows = []
	for room in rooms:
		content = {}
		content['classroom_id'] = room.classroom_id
		content['size'] = room.size
		if room.category == 0:
			content['type'] = '普通课室'
		elif room.category == 1:
			content['type'] = '多媒体课室'
		elif room.category == 2:
			content['type'] = '多媒体互动录播课室'
		devices = device.objects.filter(storage_location = room.classroom_id, is_stable = True)
		device_list = ""
		maps = {0:"多媒体",1:"桌椅",2:"其他"}
		if devices:
			devices = devices.values_list('device_type', 'device_name').annotate(device_count = Count('id'))
			for d in devices:
				string = str(d[1]) + ":" + str(d[2]) + ", "
				device_list += string
		content['devices'] = device_list
		rows.append(content)
	return JsonResponse({
		'total' : total,
		'rows' : rows,
		'code' : '200',
		'status' : 'success',
		'message' : '请求成功',
	})

def search_classroom_page(request):
	name = request.user.username
	email = request.user.email
	return render(request, 'user/search.html', {'name' : name, 'email':email})

