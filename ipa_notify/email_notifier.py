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

import email
import logging
import smtplib
from datetime import datetime

from jinja2 import Environment


class EmailNotifier:
	"""
	E-mail notification class
	"""

	# pylint: disable=too-many-arguments

	def __init__(self, host: str, port: int, user: str, password: str, from_email: str, template_env: Environment):
		self.host = host
		self.port = port
		self.user = user
		self.password = password
		self.from_email = from_email
		self.template_env = template_env

	def notify_expiration(self, send_to: str, date: datetime, days: int) -> None:
		"""
		Expiration notification function
		:param send_to: str. email address to send to
		:param date: str. password expiration date
		:param days: int. how many days until expiration
		"""
		if days > 0:
			email_message = self.template_env.get_template('expired_password.j2')
			rendered_message = email_message.render(left_days=days, expire_date=date)
		else:
			email_message = self.template_env.get_template('expired_password.j2')
			rendered_message = email_message.render(expire_date=date)

		self._send_email(send_to, rendered_message)

	def notify_locked_users(self, send_to: str, users: list) -> None:
		"""
		Notify admin about locked out users
		:param send_to: str. Admin e-mail address
		:param users: list of str. locked out user list
		"""
		email_message = self.template_env.get_template('locked_users.j2')
		rendered_message = email_message.render(users=users)

		self._send_email(send_to, rendered_message)

	def _send_email(self, send_to: str, email_content: str) -> None:
		"""
		Generic e-mail sender function
		:param send_to: str. recipient email address
		:param subject: str. email subject
		:param body: str. email body
		"""
		email_msg_str = f"From: {self.from_email}\nTo: {send_to}\n" + email_content
		msg = email.message_from_string(email_msg_str)

		# Send the message via our own SMTP server.
		try:
			smtp_conn = smtplib.SMTP(self.host, self.port)
		except smtplib.SMTPConnectError as err:
			logging.error("error connecting SMTP server: %s", err)
			return

		try:
			smtp_conn.ehlo()
			smtp_conn.starttls()
			smtp_conn.login(self.user, self.password)

			smtp_conn.send_message(msg)
		except smtplib.SMTPException as err:
			logging.error("SMTP Error: %s", err)
			return
		finally:
			smtp_conn.quit()
