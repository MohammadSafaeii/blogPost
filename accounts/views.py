from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.views.generic.edit import CreateView


class SignUpView(CreateView):
	form_class = UserCreationForm
	template_name = 'registration/signup.html'

	def form_valid(self, form):
		# Save the new user
		user = form.save()
		# Log in the user
		login(self.request, user)
		# Redirect to the blogs page
		return redirect('blog_list')