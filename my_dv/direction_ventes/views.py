from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail


# Create your views here.
def home(request):
    return render(request, "index.html")

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
        
        myuser.save()
        
        messages.success(request,"Your Account has been created successfully.")
        
        
        # welcome Email
        subject = "Welcome to GFG - Django Login!!"
        message = "Hello" + myuser.firstname + "!! \n" + "Welcome to GFG!! \n Thank you for visiting our website \n We have also sent you a confirmation email, please confirm your email address in order to activate your account. \n\n Thanking You\n Anubhav Madhav"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        
        
        return redirect('signin')
        
    return render(request, "signup.html")

def signin(request):
    
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            firstname = user.firstname
            return redirect(request,"authentication/index.html", {'firstname':firstname})
            
        else:
            messages.error(request, "Invalid username or password")
            return redirect('home')
    
    return render(request, "signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Logged Out successfully!")
    return redirect('home')