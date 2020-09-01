import logging
import smtplib
from email.message import EmailMessage


class Notifier:

	def __init__(self, host, port, user, password, from_email):
		self.host = host
		self.port = port
		self.user = user
		self.password = password
		self.from_email = from_email

	def notify_expiration(self, to, date, days):
		if days > 0:
			subject = f"Password will expire in {days} days"
			body = f"Your password will expire on {date}"
		else:
			subject = f"Your password expired"
			body = f"Your password expired on {date}"

		self._send_email(to, subject, body)

	def notify_locked_users(self, to, users):
		subject = "Locked Users"
		body = "Following users are locked"
		for user in users:
			body += "\n" + user['uid'][0]

		self._send_email(to, subject, body)

	def _send_email(self, to, subject, body):
		msg = EmailMessage()

		# me == the sender's email address
		# you == the recipient's email address
		msg['Subject'] = subject
		msg['From'] = self.from_email
		msg['To'] = to

		msg.set_content(body)

		# Send the message via our own SMTP server.
		s = smtplib.SMTP(self.host, self.port)
		s.ehlo()
		s.starttls()
		try:
			s.login(self.user, self.password)
		except smtplib.SMTPException as e:
			logging.error(f"smtp auth error: {str(e)}")
			return

		s.send_message(msg)
		s.quit()
