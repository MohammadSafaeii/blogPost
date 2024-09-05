from django.shortcuts import redirect


class LoginRedirectMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		if not request.user.is_authenticated and '/blogs/' in request.path:
			return redirect('/accounts/login/')
		return self.get_response(request)
