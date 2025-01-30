from  django.http import HttpResponse
from django.shortcuts import render,redirect
from web_app.models import *
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

    return render(request, 'face/login.html')

def LogoutPage(request):
    # del request.session['userid']
    messages.success(request, 'You have  logged Out  Successfully.')
    return redirect('/')