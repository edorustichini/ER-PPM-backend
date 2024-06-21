from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import Recipe, Comment, UserProfile
class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            'recipe_name',
            'description',
            'ingredients',
            'preparation_instructions',
            'cooking_instructions',
            'cooking_time',
            'difficulty',
            'categories',
            'calories',
            'image'
        ]
        widgets = {
            'recipe_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'ingredients': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'preparation_instructions': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'cooking_instructions': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'cooking_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'categories': forms.Select(attrs={'class': 'form-control'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'})
        }

    def clean_calories(self):
        calories = self.cleaned_data.get('calories')
        if calories and calories < 0:
            raise forms.ValidationError('Calories cannot be negative.')
        return calories

    def clean_cooking_time(self):
        cooking_time = self.cleaned_data.get('cooking_time')
        if cooking_time <= 0:
            raise forms.ValidationError('Cooking time must be greater than zero.')
        return cooking_time

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_content']
        widgets = {
            'comment_content': forms.Textarea(attrs={'rows': 2}),
        }

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(max_length=150, required=True)
    password1 = forms.CharField(required=True, widget=forms.PasswordInput)
    password2 = forms.CharField(required=True, widget=forms.PasswordInput)
    

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(required=True ,widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserChangeFormExtended(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')  # Aggiungi i campi aggiuntivi del profilo che vuoi permettere di modificare

    # Aggiungi eventuali campi personalizzati per la modifica del profilo
    # Esempio:
    
    # date_of_birth = forms.DateField(label='Date of Birth', required=False)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['email' ,'bio', 'profile_image']