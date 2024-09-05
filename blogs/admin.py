from django.contrib import admin
from .models import Blog, RatingBin, UserRating


class BlogAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'content', 'average', 'rating_count', 'created_at')


class RatingBinAdmin(admin.ModelAdmin):
	list_display = ('id', 'blog', 'average', 'rating_count', 'created_at')


class UserRatingAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'blog', 'rating_bin', 'rate', 'created_at')


admin.site.register(Blog, BlogAdmin)
admin.site.register(RatingBin, RatingBinAdmin)
admin.site.register(UserRating, UserRatingAdmin)
