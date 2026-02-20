from django.contrib import admin
from .models import Post, Category, Comment, Like, UserProfile

# ===========================================
# CATEGORY
# ===========================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)


# ===========================================
# POST
# ===========================================
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'author')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'


# ===========================================
# COMMENT
# ===========================================
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'approved', 'created_at')
    list_filter = ('approved', 'created_at')
    search_fields = ('content', 'author__username')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'


# ===========================================
# LIKE
# ===========================================
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')
    search_fields = ('post__title', 'user__username')
    ordering = ('-created_at',)


# ===========================================
# USER PROFILE
# ===========================================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__email')