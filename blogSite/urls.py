from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
	path("", RedirectView.as_view(url='/blogs/', permanent=False)),
	path("admin/", admin.site.urls),
	path("blogs/", include("blogs.urls")),
	path("accounts/", include("accounts.urls")),
]
