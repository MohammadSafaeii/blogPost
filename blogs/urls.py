from django.urls import path
from .views import BlogListView, BlogDetailView, RateBlogAPIView

urlpatterns = [
	path("", BlogListView.as_view(), name="blog_list"),
	path("<int:pk>/", BlogDetailView.as_view(), name="blog_detail"),
	path('<int:blog_id>/rate/', RateBlogAPIView.as_view(), name='rate_blog'),
]
