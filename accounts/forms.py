from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


# -----------------------------
# Signup Form
# -----------------------------

class SignupForm(UserCreationForm):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control"
        })
    )

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control"
        })
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control"
        })
    )

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control"
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control"
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control"
        })
    )

    class Meta:

        model = User

        fields = [

            "first_name",

            "last_name",

            "username",

            "email",

            "password1",

            "password2",

        ]


# -----------------------------
# Login Form
# -----------------------------

class LoginForm(forms.Form):

    username = forms.CharField(

        label="Username",

        widget=forms.TextInput(attrs={

            "class": "form-control",

            "placeholder": "Enter Username"

        })

    )

    password = forms.CharField(

        widget=forms.PasswordInput(attrs={

            "class": "form-control",

            "placeholder": "Enter Password"

        })

    )


# -----------------------------
# Profile Form
# -----------------------------

class ProfileForm(forms.ModelForm):

    class Meta:

        model = Profile

        fields = [

            "profile_image",

            "phone",

            "college",

            "degree",

            "location",

            "bio",

            "skills",

            "github",

            "linkedin",

            "portfolio",

        ]

        widgets = {

            "phone": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "college": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "degree": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "location": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "bio": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4
            }),

            "skills": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),

            "github": forms.URLInput(attrs={
                "class": "form-control"
            }),

            "linkedin": forms.URLInput(attrs={
                "class": "form-control"
            }),

            "portfolio": forms.URLInput(attrs={
                "class": "form-control"
            }),

        }