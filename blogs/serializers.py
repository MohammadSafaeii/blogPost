from rest_framework import serializers
from .models import Blog, RatingBin, UserRating


class BlogListSerializer(serializers.ModelSerializer):
	class Meta:
		model = Blog
		fields = ['id', 'title', 'average', 'rating_count']


class BlogSerializer(serializers.ModelSerializer):
	class Meta:
		model = Blog
		fields = ['id', 'title', 'content', 'average', 'rating_count', 'created_at']


class RatingBinSerializer(serializers.ModelSerializer):
	blog = BlogSerializer(read_only=True)

	class Meta:
		model = RatingBin
		fields = ['id', 'blog', 'average', 'rating_count', 'created_at']


class UserRatingSerializer(serializers.ModelSerializer):
	user = serializers.PrimaryKeyRelatedField(read_only=True)
	blog = BlogSerializer(read_only=True)
	rating_bin = RatingBinSerializer(read_only=True)

	class Meta:
		model = UserRating
		fields = ['id', 'user', 'blog', 'rating_bin', 'rate', 'created_at']
		unique_together = ('user', 'blog')
