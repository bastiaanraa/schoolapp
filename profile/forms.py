from django import forms
from django.core.exceptions import ObjectDoesNotExist


from profile.models import Profile
from profile.utils import send_password_mail


class SendPasswordForm(forms.Form):
	email = forms.EmailField(required=True)

	
	def send_email(self, email, request):
		# send email using the self.cleaned_data dictionary
		u = Profile.objects.filter(email=email)
		print u
		send_password_mail(u,request)
		

	def clean(self):
		cleaned_data = super(SendPasswordForm, self).clean()
		
		try:
			u = Profile.objects.get(email=cleaned_data.get('email'))
			return cleaned_data
		except ObjectDoesNotExist, e:
			raise forms.ValidationError("Onbekend e-mailadres.")