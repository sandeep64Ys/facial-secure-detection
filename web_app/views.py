from  django.http import HttpResponse
from django.shortcuts import render,redirect
from web_app.models import *
import base64
import pickle
import numpy as np
from io import BytesIO
from django.http import JsonResponse
import base64
import pickle
import numpy as np
from io import BytesIO
from django.http import JsonResponse
from django.shortcuts import render
from PIL import Image
import face_recognition
import cv2
from django.http import StreamingHttpResponse
from django.db.models import Sum, F
import numpy as np
import face_recognition
import pygame
import time
from datetime import datetime
from datetime import timedelta
import openpyxl 
from io import BytesIO
from datetime import timedelta
from django.contrib import messages
def login_view(request):
    if request.method == 'POST':
        usname = request.POST.get('username')
        passd = request.POST.get('password')

        # Check if the username and password match the default admin credentials
        if usname == 'admin' and passd == 'admin@123':
            # Set session for admin user
            request.session['usersession'] = True
            request.session['userid'] = usname
            request.session['u_id'] = 'admin'  # or any identifier for admin
            messages.success(request, 'You have successfully logged in as admin.')
            return redirect("/face/home")
        else:
            messages.error(request, 'You have Not Used Valid Credentials.')

    return render(request, 'login.html')

def LogoutPage(request):
    # del request.session['userid']
    messages.success(request, 'You have  logged Out  Successfully.')
    return redirect('/')
def home(request):
    return render(request,'face/home.html')

def calculate_worked_hours(attendance_time, out_time):
    att_hour, att_minute, att_second = map(int, attendance_time.split(':'))
    out_hour, out_minute, out_second = map(int, out_time.split(':'))

    # Convert both times into total seconds
    attendance_seconds = att_hour * 3600 + att_minute * 60 + att_second
    out_seconds = out_hour * 3600 + out_minute * 60 + out_second

    # Calculate worked seconds
    worked_seconds = out_seconds - attendance_seconds

    # Handle cases where out time is the next day
    if worked_seconds < 0:
        worked_seconds += 24 * 3600  # Add 24 hours in seconds

    return timedelta(seconds=worked_seconds)

def calculate_salary_per_employee(name):
    attendances = Attendance.objects.filter(name=name)
    total_hours = timedelta()
    attendance_details = []  # List to hold detailed records for the employee

    for attendance in attendances:
        try:
            # Get the corresponding out record for the attendance
            out_record = Attendance_out.objects.get(date=attendance.date, time__gte=attendance.time)
            
            # Calculate worked hours using the previously defined function
            worked_hours = calculate_worked_hours(str(attendance.time), str(out_record.time))
            total_hours += worked_hours
            
            # Append details to the list, including attendance date
            attendance_details.append({
                'attendance_time': str(attendance.time),
                'out_time': str(out_record.time),
                'worked_hours': worked_hours,
                'date': str(attendance.date),
            })

            print(f"Attendance Date: {attendance.date}, Attendance Time: {attendance.time}, Out Time: {out_record.time}, Worked Hours: {worked_hours}")

        except Attendance_out.DoesNotExist:
            print(f"No out record found for attendance on {attendance.date} at {attendance.time}")
            continue

    # Calculate total salary based on total worked hours
    total_salary = round((total_hours.total_seconds() / 3600) * 57.69, 2) # Update with your hourly rate
     
    print(f"Total Worked Hours: {total_hours}, Total Salary: {total_salary}")
    
    return {
        'total_salary': total_salary,
        'attendance_details': attendance_details
    }

def calculate_monthly_salary(name, month, year):
    attendances = Attendance.objects.filter(name=name, date__month=month, date__year=year)
    total_hours = timedelta()

    for attendance in attendances:
        try:
            out_record = Attendance_out.objects.get(date=attendance.date, time__gte=attendance.time)
            worked_hours = calculate_worked_hours(str(attendance.time), str(out_record.time))
            total_hours += worked_hours
            
        except Attendance_out.DoesNotExist:
            continue

    # Calculate total salary for the month
    # total_salary = (total_hours.total_seconds() / 3600) * 57.69  # Update with your hourly rate
    total_salary = round((total_hours.total_seconds() / 3600) * 57.69, 2)
    return total_salary

def salary_view(request):
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))
    selected_employee = request.GET.get('employee', None)

    # Get unique employee names from attendance records
    employee_names = Attendance.objects.values_list('name', flat=True).distinct()
    salary_data = []
    worked_hours_data = []

    for name in employee_names:
        # Skip employees not matching the selected employee, if any
        if selected_employee and name != selected_employee:
            continue
        
        salary_info = calculate_salary_per_employee(name)
        monthly_salary = calculate_monthly_salary(name, month, year)

        salary_data.append({
            'name': name,
            'salary': salary_info['total_salary'],
            'monthly_salary': monthly_salary,
            'attendance_details': salary_info['attendance_details'],
        })

        # Collect worked hours data for graph
        for detail in salary_info['attendance_details']:
            worked_hours_data.append({
                'date': detail['date'],
                'worked_hours': detail['worked_hours']
            })

    # Create a list of months for the dropdown
    months = list(range(1, 13))  # Months from 1 to 12

    return render(request, 'face/salary.html', {
        'salary_data': salary_data,
        'selected_month': month,
        'selected_year': year,
        'months': months,
        'employee_names': employee_names,
        'selected_employee': selected_employee,
        'worked_hours_data': worked_hours_data  # Pass worked hours data
    })

def salary_chart(request):
    selected_month = int(request.GET.get('month', datetime.now().month))
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_employee = request.GET.get('employee', None)

    # Fetch salary data based on selected month, year, and employee
    employee_names = Attendance.objects.values_list('name', flat=True).distinct()
    salary_data = []

    for name in employee_names:
        # Skip employees not matching the selected employee, if any
        if selected_employee and name != selected_employee:
            continue
        
        salary_info = calculate_salary_per_employee(name)
        monthly_salary = calculate_monthly_salary(name, selected_month, selected_year)

        salary_data.append({
            'name': name,
            'salary': salary_info['total_salary'],
            'monthly_salary': monthly_salary,
            'attendance_details': salary_info['attendance_details'],
        })

    context = {
        'salary_data': salary_data,
        'selected_month': selected_month,
        'selected_year': selected_year,
    }
    
    return render(request, 'face/salary_chart.html', context)

def export_salary_report(request):
    # Get the selected month and year
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))
    
    # Get salary data the same way as in your salary_view
    employee_names = Attendance.objects.values_list('name', flat=True).distinct()
    salary_data = []

    for name in employee_names:
        salary_info = calculate_salary_per_employee(name)
        monthly_salary = calculate_monthly_salary(name, month, year)
        
        salary_data.append({
            'name': name,
            'salary': salary_info['total_salary'],
            'monthly_salary': monthly_salary,
            'attendance_details': salary_info['attendance_details'],
        })

    # Create an Excel workbook and a worksheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Salary Report"

    # Define the headers
    headers = ['Employee Name', 'Total Salary', 'Monthly Salary', 'Date', 'Attendance Time', 'Out Time', 'Worked Hours']
    sheet.append(headers)

    # Fill in the data
    for employee in salary_data:
        for detail in employee['attendance_details']:
            row = [
                employee['name'],
                employee['salary'],
                employee['monthly_salary'],
                detail['date'],
                detail['attendance_time'],
                detail['out_time'],
                detail['worked_hours']
            ]
            sheet.append(row)

    # Save the workbook to a BytesIO stream
    output = BytesIO()
    workbook.save(output)
    output.seek(0)  # Go to the beginning of the BytesIO stream

    # Create an HTTP response with the Excel file
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=salary_report.xlsx'
    return response


def index(request):
    return render(request,"index.html")
# Create your views here.
def category_d(request):
    if request.method=="POST":
        #take as foring key trnsaction
        cat_name=request.POST.get("cat_name")
        cat_discription=request.POST.get("cat_discription")
        salary=request.POST.get("salary")
        
        c=category()

        c.cat_name=cat_name
        c.cat_discription=cat_discription
        c.cat_salary=salary
        
        c.save()
        
    return render(request,"face/category_form.html")

def employee_d(request):
    if request.method=="POST":
        #take as foring key trnsaction
        emp_name=request.POST.get("emp_name")
        Address=request.POST.get("emp_address")
        contact_no=request.POST.get("emp_no")
        emp_image=request.POST.get("image")
        cat_id=request.POST.get("cat_id")
        cid=category.objects.get(id=cat_id)
        emp_dob=request.POST.get("dob")
        emp_gender=request.POST.get("gender")
        image_data = request.POST.get('cap_image')
        if not emp_name or not image_data:
            return JsonResponse({'status': 'Name or image data missing'}, status=400)
        
        # Decode the base64 image data
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        image = np.array(image)
        
        # Convert image to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Find face encodings
        face_encodings = face_recognition.face_encodings(rgb_image)
        if not face_encodings:
            return JsonResponse({'status': 'No face detected'}, status=400)
        
        # Use the first face encoding
        encoding = face_encodings[0]
        encoding_data = pickle.dumps(encoding)
        

        
        e=employee_details()

        e.emp_name=emp_name
        e.emp_address=Address
        e.emp_contact=contact_no
        e.emp_image=emp_image
        e.categoryid=cid
        e.emp_dob=emp_dob
        e.emp_gender=emp_gender
        e.face_encoding=encoding_data

        e.save()
    return render(request,"face/employee_form.html",{"cview":category.objects.all()})

def customer_d(request):
    if request.method=="POST":
        #take as foring key trnsaction
        cust_name=request.POST.get("cust_name")
        cust_no=request.POST.get("cust_no")
        cust_address=request.POST.get("cust_address")
        
        cust=customer_details()

        cust.cust_name=cust_name
        cust.cust_contact=cust_no
        cust.cust_address=cust_address
        
        cust.save()
        
    return render(request,"face/customer_form.html")

def service_d(request):
    if request.method=="POST":
        #take as foring key trnsaction
        cust_id=request.POST.get("cust_id")
        cs=customer_details.objects.get(id=cust_id)
        done_by=request.POST.get("service_by")
        cid=employee_details.objects.get(id=done_by)
        date=request.POST.get("date")
        amount=request.POST.get("amount")

        
        s=service_done()

        s.cust_id=cs
        s.done_by=cid
        s.date=date
        s.amount=amount
        
        s.save()
    
    return render(request,"face/service_form.html",{"cview":employee_details.objects.all(),"cust":customer_details.objects.all()})

def attendence_d(request):
    if request.method=="POST":
        #take as foring key trnsaction
        attend_of=request.POST.get("attend_of")
        cid=customer_details.objects.get(attend_of)
        date=request.POST.get("date")
        time=request.POST.get("time")
        log_type=request.POST.get("log_type")

        
        a=Attendance_details()

        a.attend_of=attend_of
        a.date=date
        a.time=time
        a.log_type=log_type
        
        a.save()
    
    return render(request,"face/attendence_form.html",{"cview":employee_details.objects.all()})



def cat_view(request):
    cview=category.objects.all()
    return render(request,"face/category_view.html",{"cview":cview})

def emp_view(request):
    cview=employee_details.objects.all()
    return render(request,"face/employee_view.html",{"cview":cview})

def cust_view(request):
    cview=customer_details.objects.all()
    return render(request,"face/customer_view.html",{"cview":cview})

def serv_view(request):
    cview=service_done.objects.all()
    return render(request,"face/service_view.html",{"cview":cview})

def attend_view(request):
    cview=Attendance_details.objects.all()
    return render(request,"face/attendence_view.html",{"cview":cview})

# Initialize the pygame mixer
pygame.mixer.init()
alert_sound = pygame.mixer.Sound("thank-you.mp3")

# Load the encoded file
# print("Loading Encoded File...")
# with open("EncodeFile.p", "rb") as file:
#     encodeListKnownWithStudentNames = pickle.load(file)
# encodeListKnown, studentNames = encodeListKnownWithStudentNames
# print("Loaded Encoded File.")

# Function to mark attendance in MySQL and CSV
def markAttendance(name):
    now = datetime.now()
    dtString = now.strftime("%H:%M:%S")
    dateString = now.strftime("%Y-%m-%d")

    if not Attendance.objects.filter(name=name, date=dateString).exists():
        Attendance.objects.create(name=name, time=dtString, date=dateString)

        with open("Attendance.csv", "a") as f:
            f.write(f"\n{name},{dtString},{dateString}")

        alert_sound.play()
        time.sleep(5)  # Allow sound playback
        print(f"{name} marked attendance successfully.")
    else:
        print(f"{name} already marked attendance today.")


def markAttendanceout(name):
    now = datetime.now()
    dtString = now.strftime("%H:%M:%S")
    dateString = now.strftime("%Y-%m-%d")

    if not Attendance_out.objects.filter(name=name, date=dateString).exists():
        Attendance_out.objects.create(name=name, time=dtString, date=dateString)

        with open("Attendance_out.csv", "a") as f:
            f.write(f"\n{name},{dtString},{dateString}")

        alert_sound.play()
        time.sleep(5)  # Allow sound playback
        print(f"{name} marked Logout successfully.")
    else:
        print(f"{name} already Logout attendance today.")

# View to handle video feed

# face_recognition_attendance/attendance/views.py

def video_feed(request):
    def generate_frames():
        cap = cv2.VideoCapture(0)  # Use RTSP URL if needed
        
        if not cap.isOpened():
            print("Error: Could not open video capture.")
            return

        marked_faces = set()
        while True:
            success, img = cap.read()
            if not success:
                print("Error: Could not read frame from camera.")
                break

            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

            name = "Unknown"

            # Load encodings from the database
            employees = employee_details.objects.all()
            encodeListKnown = [pickle.loads(emp.face_encoding) for emp in employees]
            studentNames = [emp.emp_name for emp in employees]

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=0.6)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

                if True in matches:
                    matchIndex = np.argmin(faceDis)
                    name = studentNames[matchIndex].upper()

                    if name not in marked_faces:
                        markAttendance(name)
                        marked_faces.add(name)

                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            if not encodesCurFrame:
                marked_faces.clear()
                name = "Unknown"

            ret, buffer = cv2.imencode(".jpg", img)
            if not ret:
                print("Error: Could not encode image.")
                continue

            frame = buffer.tobytes()
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                   b"Content-Type: text/plain\r\n\r\n" + name.encode("utf-8") + b"\r\n")

        cap.release()  # Release the camera resource when done

    return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

def video_feed_out(request):
    def generate_frames():
        cap = cv2.VideoCapture(0)  # Use RTSP URL if needed
        
        if not cap.isOpened():
            print("Error: Could not open video capture.")
            return

        marked_faces = set()
        while True:
            success, img = cap.read()
            if not success:
                print("Error: Could not read frame from camera.")
                break

            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

            name = "Unknown"

            # Load encodings from the database
            employees = employee_details.objects.all()
            encodeListKnown = [pickle.loads(emp.face_encoding) for emp in employees]
            studentNames = [emp.emp_name for emp in employees]

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=0.6)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

                if True in matches:
                    matchIndex = np.argmin(faceDis)
                    name = studentNames[matchIndex].upper()

                    if name not in marked_faces:
                        markAttendanceout(name)
                        marked_faces.add(name)

                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            if not encodesCurFrame:
                marked_faces.clear()
                name = "Unknown"

            ret, buffer = cv2.imencode(".jpg", img)
            if not ret:
                print("Error: Could not encode image.")
                continue

            frame = buffer.tobytes()
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                   b"Content-Type: text/plain\r\n\r\n" + name.encode("utf-8") + b"\r\n")

        cap.release()  # Release the camera resource when done

    return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')
