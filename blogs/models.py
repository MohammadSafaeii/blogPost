from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Blog(models.Model):
	title = models.CharField(max_length=255)
	content = models.TextField()
	average = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
	rating_count = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title


class RatingBin(models.Model):
	blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
	average = models.DecimalField(max_digits=3, decimal_places=1)
	rating_count = models.PositiveIntegerField(default=0)
	need_update = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	# weight_based_on_average = models.FloatField()
	# weight_based_on_rating_count = models.FloatField()
	#
	# @property
	# def total_weight(self):
	# 	return self.weight_based_on_average * self.weight_based_on_rating_count


class UserRating(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
	rating_bin = models.ForeignKey(RatingBin, on_delete=models.SET_NULL, null=True, blank=True)
	rate = models.PositiveIntegerField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('user', 'blog')
