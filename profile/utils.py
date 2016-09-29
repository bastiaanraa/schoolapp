from django.core import mail 
from django.template.loader import get_template


def send_password_mail(queryset,request):

		# WAT ALS GEBRUIKS HUN EMAIL AANGEPAST HEBBEN???
		connection = mail.get_connection()

		# Manually open the connection
		connection.open()

		template_text = get_template('send_password.txt')
		template_html = get_template('send_password.html')
		messages = []
		for user in queryset:
			if user.email:
				text_content = template_text.render({"voornaam": user.first_name,"wachtwoord": user.make_pw_hash(user.username), "email": user.username}, request)
				html_content = template_html.render({"voornaam": user.first_name,"wachtwoord": user.make_pw_hash(user.username), "email": user.username}, request)
				message = mail.EmailMultiAlternatives('Login gegevens voor steinerschoolgent.be', 
							text_content, 
							'steinerschoolgent website <website@steinerschoolgent.be>',
							[user.email]
							)
				message.attach_alternative(html_content, "text/html") 
				messages.append(message)

		# Send the two emails in a single call -
		connection.send_messages(messages)
		# The connection was already open so send_messages() doesn't close it.
		# We need to manually close the connection.
		connection.close()