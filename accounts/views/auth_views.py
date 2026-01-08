from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django import forms
from django.contrib.auth import get_user_model

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)
            return redirect("post_login_redirect")
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "accounts/login.html")


def post_login_redirect(request):
    user = request.user

    if user.is_superuser:
        return redirect("/admin/")

    if user.role == "manager":
        return redirect("manager_dashboard")

    if user.role == "student":
        return redirect("student_dashboard")

    return redirect("login")


def logout_view(request):
    logout(request)
    return redirect("login")


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password'}))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        user_model = get_user_model()

        if not user_model.objects.filter(email=email).exists():
            raise forms.ValidationError("Email not registered")