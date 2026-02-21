from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

# ===========================================
# CATEGORY
# ===========================================
class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

# ===========================================
# BLOG POST
# ===========================================
class Post(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Rich text content for the blog")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PUBLISHED)
    featured_image = models.ImageField(upload_to='posts/', blank=True, null=True)
    def save(self, *args, **kwargs):
        if self.featured_image:
            img = Image.open(self.featured_image)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            if img.width > 800 or img.height > 800:
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            self.featured_image = InMemoryUploadedFile(
                buffer, 'ImageField', self.featured_image.name, 'image/jpeg', buffer.tell(), None
            )
        super().save(*args, **kwargs)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

# ===========================================
# COMMENT
# ===========================================
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment on {self.post.title}"

# ===========================================
# LIKE
# ===========================================
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['post', 'user'], name='unique_like_per_user')
        ]

    def __str__(self):
        return f"Like {self.post.title} by {self.user.username}"

# ===========================================
# USER PROFILE
# ===========================================
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    banner = models.ImageField(upload_to='banners/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.avatar:
            img = Image.open(self.avatar)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            if img.width > 800 or img.height > 800:
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            self.avatar = InMemoryUploadedFile(
                buffer, 'ImageField', self.avatar.name, 'image/jpeg', buffer.tell(), None
            )
        if self.banner:
            img = Image.open(self.banner)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            if img.width > 1200 or img.height > 400:
                img.thumbnail((1200, 400), Image.Resampling.LANCZOS)
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            self.banner = InMemoryUploadedFile(
                buffer, 'ImageField', self.banner.name, 'image/jpeg', buffer.tell(), None
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Profile"