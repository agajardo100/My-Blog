from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib import messages

from .forms import UserLoginForm, UserRegisterForm
# Create your views here.

#TODO: Profile page

def login_view(request):
    #If already logged in, redirect to home
    if request.user.is_authenticated():
        return redirect("/")

    next_page = request.GET.get('next')

    title = "Login"
    form = UserLoginForm(request.POST or None)

    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        login(request, user)
        if next_page:
            return redirect(next_page)
        if user.is_authenticated():
            messages.success(request, "Login successful. Welcome back.")
        return redirect("/")
    context = {
        'form': form,
        'title': title,
    }
    return render(request, "form.html", context)    #"registration/login.html"


def logout_view(request):
    #If user not logged in, redirect to home
    if not request.user.is_authenticated():
        return redirect("/")

    logout(request)
    return render(request, "success.html", {'title': "Logged Out", 'success_message':"Logged out successfully."} )


def register_view(request):
    #If already logged in, redirect to home
    if request.user.is_authenticated():
        return redirect("/")

    next_page = request.GET.get('next')

    title = "Register"
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        new_user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        new_user.set_password(password)
        new_user.save()
        login(request, new_user)

        if next_page:
            return redirect(next_page)

        return render(request, "success.html", {'title': "Registration Complete.", 'success_message':"Welcome to my blog!"})

    context = {
        'title': title,
        'form': form,
    }
    return render(request, "form.html", context)
