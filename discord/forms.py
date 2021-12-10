from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Message, User


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']


class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ['name', 'bio', 'avatar']


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['user', 'participants']


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['body']
