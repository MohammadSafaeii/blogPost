from celery import shared_task
from django.contrib.auth.models import User
from .models import Blog, UserRating


@shared_task
def create_or_update_rating(user_id, blog_id, rate):
	user = User.objects.get(id=user_id)
	blog = Blog.objects.get(id=blog_id)

	UserRating.objects.update_or_create(
		user=user,
		blog=blog,
		defaults={'rate': rate}
	)