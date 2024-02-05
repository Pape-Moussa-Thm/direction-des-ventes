from base64 import urlsafe_b64decode
from email.message import EmailMessage
from django.conf import Settings
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str

from .tokens import generate_token


# Create your views here.
def home(request):
    return render(request, "authentication/index.html")

def signup(request):
    
    if request.method == "POST":
        # username = request.POST.get('username')
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']
        confirmpassword = request.POST['confirmpassword']   
        
        if User.objects.filter(username=username):
            messages.error(request, "Username already exists! Please try some other username")
            return redirect('home')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('home')
        
        if len(username)>10:
            messages.error(request, "Username must be under 10 characters")
            
        
        if password!= confirmpassword:
            messages.error(request, "Passwords didn't match!")
            
        if not username.isalnum():
            messages.error(request, "Username must be alpha-numeric!")
            return redirect('home')    

        myuser = User.objects.create_user(username,email,password)
        
        myuser.confirmpassword = confirmpassword
        myuser.firstname = firstname
        myuser.lastname = lastname
        myuser.is_active = False
        myuser.save()
        
        messages.success(request,"Your Account has been successfully created. We have sent you a confirmation email, please confirm you email in order to activate your account.")
        
        
        # welcome Email
        subject = "Welcome to GFG - Django Login!!"
        message = "Hello" + myuser.firstname + "!! \n" + "Welcome to GFG!! \n Thank you for visiting our website \n We have also sent you a confirmation email, please confirm your email address in order to activate your account. \n\n Thanking You\n Pape Thiam"
        from_email = Settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        
        
        # Email Address Confirmation Email
        
        current_site = get_current_site(request)
        email_subject = "confirm your email @ GFG - Django Login!!"
        message2 = render_to_string('email_confirmation.html',{
            'name':myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser),
        })
        email = EmailMessage(
            email_subject, 
            message2, Settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()
        
        
        return redirect('signin')
        
    return render(request, "authentication/signup.html")

def signin(request):
    
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            firstname = user.firstname
            return redirect(request,"index.html", {'firstname':firstname})
            
        else:
            messages.error(request, "Invalid username or password")
            return redirect('home')
    
    return render(request, "authentication/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Logged Out successfully!")
    return redirect('home')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_b64decode(uidb64))

        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError,  OverflowError, User.DoesNotExist):
        myuser = None
        
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')
    
    