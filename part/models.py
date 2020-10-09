from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class academy(models.Model):
	#采用django默认创建的自增主键
	academy_name = models.CharField(max_length=20, null=False)						#学院名称
	academy_area = models.CharField(max_length=20, null=False)						#所在校区
	
class major(models.Model):
	#采用django默认创建的自增字段
	college = models.ForeignKey(academy, on_delete=models.DO_NOTHING,  related_name = 'major_academy')				#隶属学院
	major_name = models.CharField(max_length=20, null=False)

class student(models.Model):
	user = models.OneToOneField(User,on_delete=models.CASCADE) 						#对应于一条user记录，存放了账号、密码、邮箱
	student_name = models.CharField(max_length=20,null=False) 						#学生姓名		
	academy = models.ForeignKey(academy,on_delete=models.DO_NOTHING, related_name = 'student_academy')				#隶属学院
	major = models.ForeignKey(major,on_delete=models.DO_NOTHING, related_name = 'student_major')					#所属专业
	phone = models.CharField(max_length=20, null=False)								#联系方式
	status = models.BooleanField(null=False,default=True)							#账号状态 有效=1 失效=0 
	create_time = models.DateTimeField(auto_now_add=True)	
	class Meta:
		ordering = ['create_time'] 

class teacher(models.Model):
	user = models.OneToOneField(User,on_delete=models.CASCADE)						#对应user，存放了账号、密码、邮箱
	teacher_name = models.CharField(max_length=20,null=False)						#老师姓名
	academy = models.ForeignKey(academy,on_delete=models.DO_NOTHING,related_name = 'teacher_academy')						#所处学院
	phone = models.CharField(max_length=20,null=False)								#联系方式
	status = models.BooleanField(null=False,default=True)							#账号状态 有效=1 失效=0 
	create_time = models.DateTimeField(auto_now_add=True)
	class Meta:
		ordering = ['create_time']

class staff(models.Model):
	user = models.OneToOneField(User,on_delete=models.CASCADE)
	device_admin = models.BooleanField(null=False, default = False) 				#是否为设备管理员 是=1 否=0 可以通过设备审批/维修
	classroom_admin = models.BooleanField(null=False, default = False) 				#是否为课室管理员 是=1 否=0 可以通过设备审批/维修
	phone = models.CharField(max_length=20, null=False)								#联系方式
	status = models.BooleanField(null=False,default=True)							#账号状态 有效=1 失效=0 
	create_time = models.DateTimeField(auto_now_add=True)
	class Meta:
		ordering = ['create_time']

class device(models.Model):
	#device_id采用django默认创建的自增主键
	status = models.BooleanField(null=False, default=True) 							#设备可使用状态 可用=1 不可用=0
	last_check_time = models.DateTimeField(auto_now_add=True) 						#设备上次检修时间
	device_type = models.IntegerField(null = False) 								#设备所属类别 多媒体=0 桌椅=1 其他=2
	device_name = models.CharField(null = False, max_length = 20) 					#设备具体名称：话筒，小凳子，长桌等
	storage_location = models.CharField(null = False, max_length = 20) 				#设备存放地点：课室编号
	responsible_staff = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name = 'device_staff') 		#设备负责人的工号：user表的id字段
	is_stable = models.BooleanField(null = False, default = False) 					#设备是否为课室内部固定设施 固定=1 可出借=0
	
class classroom(models.Model): # 课室详情信息表
	classroom_id = models.CharField(null=False, max_length=10,primary_key = True)	#课室编号
	status = models.BooleanField(default = True, null=False)						#课室状态 可借用=1 不可借用=0
	size = models.IntegerField(null = False)										#容纳人数 目前可有20 50 80 100 120 200 的选项
	category = models.IntegerField(null=False, default = 0) 						#课室类型: 普通课室=0, 多媒体课室=1, 多媒体录播课室=2
	class Meta:
		ordering = ['classroom_id']

class device_apply(models.Model):
	#主键采用django默认创建的自增字段
	applicant = models.ForeignKey(User,on_delete=models.DO_NOTHING, related_name = 'device_applicant')		        	#申请人编号
	classroom = models.ForeignKey(classroom,on_delete=models.DO_NOTHING, related_name = 'device_apply_classroom')		    #教室编号
	device_type = models.IntegerField(null=False)									#设备类别
	device_name = models.CharField(max_length=20,null=False)						#设备名称
	use_date = models.DateField(null=False)											#需求日期
	apply_quatity = models.IntegerField(null=False)									#设备需求数目
	apply_section_begin = models.IntegerField(null=False)					        #需求开始节数：之后都统一为1-10
	apply_section_end = models.IntegerField(null=False)					        	#需求结束节数
	apply_reason = models.TextField(null=False)										#申请事由
	apply_status = models.IntegerField(null=False,default=0)		                #审批状态 提交申请=0 已过初审=1 已拒绝=3
	apply_time = models.DateTimeField(auto_now_add=True)			                #申请提交时间
	pass_time = models.DateTimeField(null=True)			                			#审批通过时间
	apply_head = models.ForeignKey(User,on_delete=models.DO_NOTHING,null=True,related_name = 'device_apply_head')		#审批人
	responsible_staff = models.ForeignKey(User,on_delete=models.DO_NOTHING,null=False,related_name = 'responsible_staff_id') 							#申批问责老师
	refuse_reason = models.TextField(null=True)										#拒绝理由
	class Meta:
		ordering = ['apply_time']

class classroom_apply(models.Model):
	#主键采用django默认创建的自增字段
	applicant = models.ForeignKey(User,on_delete=models.DO_NOTHING, related_name = 'applicant_id')		        	#申请人编号
	classroom = models.ForeignKey(classroom,on_delete=models.DO_NOTHING, related_name = 'apply_classroom')		    #教室编号
	use_date = models.DateField(null=False)											#需求日期
	apply_section_begin = models.IntegerField(null=False, default = 0)				#需求节数起点
	apply_section_end = models.IntegerField(null=False, default = 0)				#需求节数终点
	apply_reason = models.TextField(null=False)										#申请事由
	apply_status = models.IntegerField(null=False,default=0)		                #审批状态 0 1 2 3
	apply_time = models.DateTimeField(auto_now_add=True)			                #申请时间
	pass_time_1 = models.DateTimeField(null=True)			                		#初审通过时间
	pass_time_2 = models.DateTimeField(null=True)			                		#复审通过时间
	apply_head_1 = models.ForeignKey(User,on_delete=models.DO_NOTHING,null=True, related_name = 'apply_head_1')    #审批人1
	apply_head_2 = models.ForeignKey(User,on_delete=models.DO_NOTHING,null=True, related_name = 'apply_head_2')    #审批人2
	refuse_reason = models.TextField(null = True)									#需求规模：课室容纳人数	
	apply_category = models.IntegerField(null=False, default = 0) 					#需求课室类型
	apply_size = models.IntegerField(null = False)									#拒绝理由	
	responsible_teacher = models.ForeignKey(User,on_delete=models.DO_NOTHING,null=False, related_name = 'responsible_teacher_id') #申请问责老师
	class Meta:
		ordering = ['apply_time']
	
class classroom_apply_record(models.Model):
	#主键采用django默认创建的自增字段
	apply = models.ForeignKey(classroom_apply,on_delete=models.DO_NOTHING, related_name = 'classroom_apply_record')			#这件教室的使用对应了哪张申请单
	classroom = models.ForeignKey(classroom,on_delete=models.DO_NOTHING,null=False, related_name = 'classroom_record')	#教室编号
	use_date = models.DateField(null=False)											#需求日期
	apply_section_begin = models.IntegerField(null=False, default = 0)				#需求节数起点
	apply_section_end = models.IntegerField(null=False, default = 0)				#需求节数终点	
	class Meta:
		ordering = ['use_date']				

class curriculum(models.Model):
	#主键采用django默认创建的自增字段
	course_name = models.CharField(null=False, max_length=50)						#课程名称
	classroom = models.ForeignKey(classroom,on_delete=models.DO_NOTHING, related_name = 'course_classroom') 			#课室编号
	section_begin = models.IntegerField(null=False) 								#开始节数
	section_end = models.IntegerField(null=False)									#结束节数
	week_day =  models.IntegerField(null=False)										#周几上课
	academy_id = models.ForeignKey(academy,on_delete=models.DO_NOTHING, related_name = 'course_academy')				#所属学院
	

class device_broken(models.Model):
	#主键采用django默认创建的自增字段
	applicant = models.ForeignKey(User,on_delete=models.DO_NOTHING, related_name = 'device_broken_applicant')					#故障提交人
	device = models.ForeignKey(device,on_delete=models.DO_NOTHING, related_name = 'broken_device_id') 					#设备
	submit_time = models.DateField(auto_now_add=True)								#故障提交时间
	detail = models.TextField(null=True)											#故障详情
	status = models.BooleanField(null=False,default=0)								#未处理=0 已处理=1
	pass_time = models.DateField(null=True)											#故障处理完成时间
	pass_user_id = models.ForeignKey(User,on_delete=models.DO_NOTHING, related_name = 'device_amend_pass_id')				#故障处理通过人
	class Meta:
		ordering = ['submit_time']

class device_apply_record(models.Model):
	#主键采用django默认创建的自增字段
	apply = models.ForeignKey(device_apply,on_delete=models.DO_NOTHING, related_name = 'device_record_apply_id')				#对应哪一张设备申请单
	device = models.ForeignKey(device,on_delete=models.DO_NOTHING, related_name = 'device_record_id')						#设备
	use_date = models.DateField(null=False)											#使用日期
	section_begin = models.IntegerField(null=False)									#开始节数
	section_end = models.IntegerField(null=False)									#结束节数
	class Meta:
		ordering = ['use_date']

class EmailVerifyRecord(models.Model):
	code = models.CharField(max_length=20,null=False,primary_key = True)
	email = models.CharField(max_length=30,null=False)
	send_type = models.CharField(null=False, max_length=50)
	send_time = models.DateField(null=False, auto_now=True)
	class Meta:
		db_table = "EmailVerifyRecord"
