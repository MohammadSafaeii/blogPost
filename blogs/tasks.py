import pandas as pd
from statsmodels.tsa.seasonal import STL
from celery import shared_task
from django.contrib.auth.models import User
from blogSite.constants import ANOMALOUS_DATA_WEIGHT, ANOMALOUS_DATA_DETECTION_THRESHOLD
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

	should_update_blog = False

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
		should_update_blog = True

	update_rating_bins.delay(blog_id, should_update_blog)


@shared_task
def update_rating_bins(blog_id, should_update_blog):
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
		should_update_blog = True

	# check if any rating bin created or updated, we should re-calculate average
	if should_update_blog:
		update_blog.delay(blog_id)


@shared_task
def update_blog(blog_id):
	# calculate rating parameters
	blog_average, total_rating_count = calculate_rating_parameters(blog_id)

	# update blog rate fields if we have at least one rate
	if total_rating_count > 0:
		Blog.objects.filter(id=blog_id).update(average=blog_average, rating_count=total_rating_count)


def calculate_rating_parameters(blog_id):
	rating_bins = RatingBin.objects.filter(blog=blog_id)
	rating_bins_count = rating_bins.count()
	if rating_bins_count > 7:
		blog_average, total_rating_count = calculate_weight_rating_parameters(rating_bins, rating_bins_count)
	else:
		blog_average, total_rating_count = calculate_exact_rating_parameters(rating_bins)
	return blog_average, total_rating_count


def calculate_exact_rating_parameters(rating_bins):
	rating_bins_parameters = rating_bins.aggregate(
		total_sum=Sum(F('average') * F('rating_count')),
		total_rating_count=Sum('rating_count')
	)

	# Calculate new rating parameters for the blog
	total_sum = rating_bins_parameters['total_sum'] or 0
	total_rating_count = rating_bins_parameters['total_rating_count'] or 0
	blog_average = 0

	# calculate blog average if we have at least one rate
	if total_rating_count > 0:
		blog_average = total_sum / total_rating_count

	return blog_average, total_rating_count


def calculate_weight_rating_parameters(rating_bins, rating_bins_count):
	# Fetching the data sorted by 'created_at' (timestamps)
	rating_bins_sorted = rating_bins.order_by('created_at')

	# Convert the data to a pandas DataFrame
	data = pd.DataFrame({
		'Ratings': [rb.rating_count for rb in rating_bins_sorted],
		'Averages': [rb.average for rb in rating_bins_sorted]
	})

	# Perform STL decomposition
	seasonal_number = rating_bins_count if rating_bins_count % 2 != 0 else rating_bins_count + 1
	stl = STL(data['Ratings'], seasonal=seasonal_number, period=7)
	result = stl.fit()
	residuals = result.resid

	# Calculate standard deviation of residuals
	residuals_std = residuals.std()

	# Initialize variables for calculating total weighted average
	total_weighted_sum = 0
	total_weighted_rating_count = 0

	# Modify the weighting of rows with high residuals
	for i, row in data.iterrows():
		weight = 1  # Default weight
		if residuals[i] > ANOMALOUS_DATA_DETECTION_THRESHOLD * residuals_std:
			weight = ANOMALOUS_DATA_WEIGHT  # Apply lower weight to rows with high residuals (anomalies)

		# Calculate total weighted sum and total rating count
		total_weighted_sum += row['Averages'] * row['Ratings'] * weight
		total_weighted_rating_count += row['Ratings'] * weight

	# Calculate the total weighted average
	if total_weighted_rating_count > 0:
		blog_average = total_weighted_sum / total_weighted_rating_count
	else:
		blog_average = 0

	return blog_average, int(total_weighted_rating_count)

