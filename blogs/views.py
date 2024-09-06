from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.helpers import get_or_none
from .models import Blog, UserRating
from .tasks import create_or_update_user_rating
from .serializers import BlogSerializer, BlogListSerializer


class BlogListView(APIView):

	def get(self, request):
		# sort by -id to show latest blogs first
		blogs = Blog.objects.all().order_by('-id')
		serializer = BlogListSerializer(blogs, many=True)
		# compare a dict that has all user rates
		user_ratings = {
			rating.blog_id: rating.rate
			for rating in UserRating.objects.filter(user=request.user)
		}
		context = {
			'blogs': serializer.data,
			'user_ratings': user_ratings,
		}
		return TemplateResponse(request, 'blogs/blog_list.html', context)


class BlogDetailView(APIView):

	def get(self, request, pk):
		try:
			blog = Blog.objects.get(pk=pk)
		except Blog.DoesNotExist:
			raise Http404("Blog not found")
		serializer = BlogSerializer(blog)
		user_rate = get_or_none(UserRating, user=request.user, blog=blog)
		context = {
			'blog': serializer.data,
			'user_rate': user_rate
		}
		return TemplateResponse(request, 'blogs/blog_detail.html', context)


class RateBlogAPIView(APIView):

	def post(self, request, blog_id):
		blog = get_object_or_404(Blog, id=blog_id)
		rate = request.data.get('rate')

		# Use Celery task to update or create the user rating
		create_or_update_user_rating.delay(request.user.id, blog.id, rate)

		return Response({"detail": "Rating submitted successfully!"}, status=status.HTTP_200_OK)
