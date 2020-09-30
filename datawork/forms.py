from django.forms import ModelForm
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django import forms

class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="Fist name")
    last_name = forms.CharField(label="Last name")
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']

class RegisterRenterForm(ModelForm):
    class Meta:
        model= RoomRenter
        exclude = ['rr_id','user_id']

class RegisterOwnerForm(ModelForm):
    class Meta:
        model= RoomOwner
        exclude = ['ro_id','user_id']

class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['email','password',]

class AddRoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['r_title','r_type','r_rent','r_image','r_desc']

