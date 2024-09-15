from PIL import Image
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class UserForm(forms.ModelForm):
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('avatar', 'username', 'first_name', 'last_name', 'email')

    def clean_avatar(self):
        image = self.cleaned_data.get('avatar')
        if image:
            # Check image format
            try:
                img = Image.open(image)
                img.verify()  # Verify the image format
            except (IOError, SyntaxError) as e:
                raise ValidationError("Invalid image file")
            # Optionally: Check image size (e.g., must be less than 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Image file too large ( > 5MB )")
        return image
