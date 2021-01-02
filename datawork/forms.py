from django.forms import ModelForm
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import EmailValidator
from django import forms

class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email",validators=[EmailValidator],error_messages={'invalid': 'This is invalid email address!'})
    first_name = forms.CharField(label="Fist name")
    last_name = forms.CharField(label="Last name")
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']

class RegisterRenterForm(ModelForm):
    class Meta:
        model= RoomRenter
        labels = {
            "rr_contact": 'Contact',
            "rr_image": 'Image',
            "rr_street": 'Street/Road/Village',
            "rr_id_proof": 'Id Proof Image',
        }
        exclude = ['rr_id','user_id']

class RegisterOwnerForm(ModelForm):
    class Meta:
        model= RoomOwner
        labels = {
            "ro_contact": 'Contact',
            "ro_image": 'Image',
            "ro_street": 'Street/Road/Village',
            "ro_id_proof": 'Id Proof Image',
            "ro_house": 'House Name',
            "ro_house_image": 'House Image'
        }
        fields = ['ro_contact','ro_image','ro_id_proof','state','city','ro_street','ro_house','ro_house_image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].queryset = City.objects.none()

        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['city'].queryset = City.objects.filter(state__id=state_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['city'].queryset = self.instance.state.city_set.order_by('name')

class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['email','password',]

class AddRoomForm(ModelForm):
    class Meta:
        model = Room
        labels = {
            "r_title": 'Title',
            "r_type": 'Room Type',
            "r_rent": 'Rent Price',
            "r_image": 'Room Image',
            "r_desc": 'Description'
        }
        fields = ['r_title','r_type','r_rent','r_image','r_desc']

class EditRoomForm(ModelForm):
    class Meta:
        model = Room
        labels = {
            "r_title": 'Title',
            "r_type": 'Room Type',
            "r_rent": 'Rent Price',
            "r_desc": 'Description'
        }
        fields = ['r_title','r_type','r_rent','r_desc']

class RoomQueryForm(forms.ModelForm):
    class Meta:
        model = RoomQuery
        labels = {
            "m_name": 'Name',
            "m_contact": 'Contact',
            "m_message": 'Message'
        }
        exclude = ['m_id','user_id','m_doc']

class UpdateProfile(forms.ModelForm):
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="Fist name")
    last_name = forms.CharField(label="Last name")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email',]

class UpdateOwnerForm(ModelForm):
    class Meta:
        model = RoomOwner
        labels = {
            "ro_house":'House Name',
            "ro_contact": 'Contact',
            "ro_street": 'Street/Road/Village',
        }
        fields = ['ro_house','ro_contact','ro_street','state','city']

class UpdateRenterForm(ModelForm):
    class Meta:
        model = RoomRenter
        labels = {
            "rr_contact": 'Contact',
            "rr_street": 'Street/Road/Village',
        }
        fields = ['rr_contact','rr_street']

