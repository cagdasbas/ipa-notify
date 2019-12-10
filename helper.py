import smtplib
from email.message import EmailMessage


def notify_expiration(email, date, days):
	subject = "Password will expire in %d days" % days
	body = "Your password will expire on %s" % date
	send_email(email, subject, body)


def notify_locked_users(email, users):
	subject = "Locked Users"
	body = "Following users are locked"
	for user in users:
		body += "\n" + user['uid'][0]

	send_email(email, subject, body)


def send_email(email, subject, body):
	msg = EmailMessage()

	# me == the sender's email address
	# you == the recipient's email address
	msg['Subject'] = subject
	msg['From'] = "ipanotifier@ouva.co"
	msg['To'] = email

	msg.set_content(body)

	# Send the message via our own SMTP server.
	s = smtplib.SMTP('localhost')
	s.send_message(msg)
	s.quit()
