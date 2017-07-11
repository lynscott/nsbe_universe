from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

class UserSignUpForm(UserCreationForm):
    class Meta:
        fields = ('username', 'first_name', 'email','password1', 'password2')
        model = get_user_model()

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['username'].label = 'Username'
        self.fields['email'].label = 'Email'
        self.fields['first_name'].label = 'Red ID'
