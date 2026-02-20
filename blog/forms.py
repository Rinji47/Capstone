import re
from django import forms
from .models import UserProfile, Post, Category

# Form for editing user profile
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'banner']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Tell us about yourself...'
            }),
        }

class PostForm(forms.ModelForm):
    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError('Title is required.')
        if len(title) < 5:
            raise forms.ValidationError('Title must be at least 5 characters long.')
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content', '')
        # Strip HTML tags to get plain text for validation
        plain_text = re.sub(r'<[^>]+>', '', content).strip()
        if not plain_text:
            raise forms.ValidationError('Content is required.')
        if len(plain_text) < 5:
            raise forms.ValidationError('Content must be at least 5 characters long.')
        return content  # return the original HTML content

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError('Please select a category.')
        return category

    class Meta:
        model = Post
        fields = ['title', 'content', 'featured_image', 'category', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'styled-input',
                'placeholder': 'Enter post title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'styled-input',
                'placeholder': 'Write your post content here...'
            }),
            'category': forms.Select(attrs={'class': 'styled-input'}),
            'status': forms.Select(attrs={'class': 'styled-input'}),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'styled-input'}),
        }