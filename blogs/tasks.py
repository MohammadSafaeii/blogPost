from celery import shared_task
from django.contrib.auth.models import User
from .models import Blog, UserRating, RatingBin
from django.db.models import Avg, Count, Sum, F


@shared_task
def create_or_update_user_rating(user_id, blog_id, rate):
	user = User.objects.get(id=user_id)
	blog = Blog.objects.get(id=blog_id)

	user_rating, created = UserRating.objects.update_or_create(
		user=user,
		blog=blog,
		defaults={'rate': rate}
	)

	# Check if the 'rating_bin' is not None, update 'need_update' field
	if user_rating.rating_bin is not None:
		user_rating.rating_bin.need_update = True
		user_rating.rating_bin.save()


@shared_task
def updating_blogs_process():
	# Get all blogs and trigger the task to process ratings for each blog individually
	blog_ids = Blog.objects.values_list('id', flat=True)

	for blog_id in blog_ids:
		create_rating_bin.delay(blog_id)  # Trigger async tasks for each blog


@shared_task
def create_rating_bin(blog_id):
	unrated_user_ratings = UserRating.objects.filter(blog=blog_id, rating_bin__isnull=True)

	# Calculate the average rate and count for the given blog
	rate_values = unrated_user_ratings.aggregate(
		average_rate=Avg('rate'),
		rating_count=Count('id')
	)

	# Check if there are any user ratings to process
	if rate_values['rating_count'] > 0:
		# Create the RatingBin row for the blog
		rating_bin = RatingBin.objects.create(
			blog_id=blog_id,
			average=rate_values['average_rate'],
			rating_count=rate_values['rating_count']
		)
		# Update the UserRating rows to link to the RatingBin
		unrated_user_ratings.update(rating_bin=rating_bin)

	update_rating_bins.delay(blog_id)


@shared_task
def update_rating_bins(blog_id):
	# Query all RatingBin records where need_update is True
	rating_bins_to_update = RatingBin.objects.filter(blog=blog_id, need_update=True)

	for rating_bin in rating_bins_to_update:
		# Filter UserRating rows related to this RatingBin
		user_ratings = UserRating.objects.filter(rating_bin=rating_bin)

		# Calculate the new average and count
		new_average = user_ratings.aggregate(average_rate=Avg('rate'))['average_rate']

		# Update the RatingBin with the new values
		rating_bin.average = new_average
		rating_bin.need_update = False  # Reset need_update to False
		rating_bin.save()

	update_blog.delay(blog_id)


@shared_task
def update_blog(blog_id):
	# Update the average for the specific blog based on its RatingBins
	rating_bins = RatingBin.objects.filter(blog=blog_id).aggregate(
		total_weighted_average=Sum(F('average') * F('rating_count')),
		total_rating_count=Sum('rating_count')
	)

	# Calculate the new average for the blog
	total_weighted_average = rating_bins['total_weighted_average'] or 0
	total_rating_count = rating_bins['total_rating_count'] or 0

	# update blog rate fields if we have at least one rate
	if total_rating_count > 0:
		blog_average = total_weighted_average / total_rating_count
		Blog.objects.filter(id=blog_id).update(average=blog_average, rating_count=total_rating_count)
