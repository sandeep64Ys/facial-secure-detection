from django.contrib import admin
from .models import *
# Register your models here.

class cat(admin.ModelAdmin):
    list_display=('cat_name','cat_discription','cat_salary')
admin.site.register(category,cat)

class empdetails(admin.ModelAdmin):
    list_display=('emp_name','emp_address','emp_contact','emp_image','categoryid','emp_dob','emp_gender')
admin.site.register(employee_details,empdetails)

class custdetails(admin.ModelAdmin):
    list_display=('cust_name','cust_contact','cust_address')
admin.site.register(customer_details,custdetails)

class ser_doneby(admin.ModelAdmin):
    list_display=('cust_id','done_by','date','amount')
admin.site.register(service_done,ser_doneby)

class attend_details(admin.ModelAdmin):
    list_display=('attend_of','date','time','log_type')
admin.site.register(Attendance_details,attend_details)