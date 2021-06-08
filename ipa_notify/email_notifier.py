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
import ssl
from datetime import datetime
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment


class EmailNotifier:
	"""
	E-mail notification class
	"""

	# pylint: disable=too-many-arguments

	def __init__(self, host: str, port: int, security: str, user: str, password: str, from_email: str,
	             template_env: Environment):
		self.host = host
		self.port = port
		self.security = security
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
			email_message = self.template_env.get_template('expiring_password.j2')
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
		msg = email.message_from_string(email_content)

		msg_to_send = MIMEMultipart("alternative")
		msg_to_send.set_charset('utf8')

		msg_to_send['From'] = self.from_email
		msg_to_send['To'] = send_to

		msg_to_send['Subject'] = Header(
			msg['subject'].encode('utf-8'),
			'UTF-8'
		).encode()

		msg_body = MIMEText(msg.get_payload().encode('utf-8'), 'html', 'UTF-8')
		msg_to_send.attach(msg_body)

		# Send the message via our own SMTP server.
		try:
			if self.security == "SSL":
				context = ssl.create_default_context()
				smtp_conn = smtplib.SMTP_SSL(self.host, self.port, context=context)
			else:
				smtp_conn = smtplib.SMTP(self.host, self.port)
			logging.debug("smtp connection is created.")
		except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected) as err:
			logging.error("error connecting SMTP server: %s", err)
			raise ValueError()
		except ssl.SSLError as err:
			logging.error("SSL connection error %s", err)
			raise ValueError()

		try:
			smtp_conn.ehlo()
			logging.debug("ehlo is sent")
			if self.security == "STARTTLS":
				smtp_conn.starttls()
				logging.debug("starttls is started")
			if self.user != "" and self.password != "":  # don't try to login if no username/password is supplied
				smtp_conn.login(self.user, self.password)
				logging.debug("smtp login successful")

			smtp_conn.send_message(msg_to_send)
			logging.debug("smtp message is sent")
		except smtplib.SMTPRecipientsRefused as err:
			logging.error("error sending to %s error: %s", send_to, err)
			return
		except smtplib.SMTPException as err:
			logging.error("SMTP Error: %s", err)
			raise ValueError()
		finally:
			smtp_conn.quit()
