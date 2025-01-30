from django.db import models

# Create your models here.
class category(models.Model):
    cat_name=models.CharField(max_length=200,null=True)
    cat_discription=models.CharField(max_length=200)
    cat_salary=models.CharField(max_length=200)

    def __str__(self):
        return self.cat_name

class employee_details(models.Model):
    emp_name=models.CharField(max_length=200)
    emp_address=models.CharField(max_length=200)
    emp_contact=models.CharField(max_length=200)
    emp_image=models.FileField(null=True)
    categoryid=models.ForeignKey(category, on_delete=models.CASCADE,null=True)
    emp_dob=models.CharField(max_length=200)
    emp_gender=models.CharField(max_length=200)
    face_encoding = models.BinaryField()  # Store face encoding data
    def __str__(self):
        return self.emp_name
    
    def __str__(self):
         return self.categoryid.cat_name+"--"+self.emp_name

class customer_details(models.Model):
    cust_name=models.CharField(max_length=200)
    cust_contact=models.CharField(max_length=200)
    cust_address=models.CharField(max_length=200)

    def __str__(self):
        return self.cust_name
 
class service_done(models.Model):
    cust_id=models.ForeignKey(customer_details, on_delete=models.CASCADE,null=True)
    done_by=models.ForeignKey(employee_details, on_delete=models.CASCADE,null=True)
    date=models.DateField(max_length=200)
    amount=models.CharField(max_length=200)

    def __str__(self):
         return self.cust_id.cust_name+"--"+self.cust_id
    
    def __str__(self):
         return self.done_by.emp_name+"--"+self.done_by

class Attendance_details(models.Model):
    attend_of=models.ForeignKey(employee_details, on_delete=models.CASCADE,null=True)
    date=models.CharField(max_length=200)
    time=models.CharField(max_length=200)
    log_type=models.CharField(max_length=200)



class Attendance(models.Model):
    name = models.CharField(max_length=100)
    time = models.TimeField()
    date = models.DateField()
class Attendance_out(models.Model):
    name = models.CharField(max_length=100)
    time = models.TimeField()
    date = models.DateField()

