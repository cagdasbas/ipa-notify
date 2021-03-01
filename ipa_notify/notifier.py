#  Copyright (c) 2021.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
import smtplib
from datetime import datetime
from email.message import EmailMessage


class Notifier:
	"""
	E-mail notification class
	"""

	# pylint: disable=too-many-arguments

	def __init__(self, host: str, port: int, user: str, password: str, from_email: str):
		self.host = host
		self.port = port
		self.user = user
		self.password = password
		self.from_email = from_email

	def notify_expiration(self, send_to: str, date: datetime, days: int) -> None:
		"""
		Expiration notification function
		:param send_to: str. email address to send to
		:param date: str. password expiration date
		:param days: int. how many days until expiration
		"""
		if days > 0:
			subject = f"Password will expire in {days} days"
			body = f"Your password will expire on {date}"
		else:
			subject = "Your password expired"
			body = f"Your password expired on {date}"

		self._send_email(send_to, subject, body)

	def notify_locked_users(self, send_to: str, users: list) -> None:
		"""
		Notify admin about locked out users
		:param send_to: str. Admin e-mail address
		:param users: list of str. locked out user list
		"""
		subject = "Locked Users"
		body = "Following users are locked"
		for user in users:
			body += "\n" + user['uid'][0]

		self._send_email(send_to, subject, body)

	def _send_email(self, send_to: str, subject: str, body: str) -> None:
		"""
		Generic e-mail sender function
		:param send_to: str. recipient email address
		:param subject: str. email subject
		:param body: str. email body
		"""
		msg = EmailMessage()

		# me == the sender's email address
		# you == the recipient's email address
		msg['Subject'] = subject
		msg['From'] = self.from_email
		msg['To'] = send_to

		msg.set_content(body)

		# Send the message via our own SMTP server.
		smtp_conn = smtplib.SMTP(self.host, self.port)
		smtp_conn.ehlo()
		smtp_conn.starttls()
		try:
			smtp_conn.login(self.user, self.password)
		except smtplib.SMTPException as err:
			logging.error("smtp auth error: %s", err)
			return

		smtp_conn.send_message(msg)
		smtp_conn.quit()
