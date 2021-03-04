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

import argparse
import datetime
import logging
import subprocess

from python_freeipa.client_meta import ClientMeta
from python_freeipa.exceptions import Unauthorized, NotFound

from ipa_notify.email_notifier import EmailNotifier


class IPAAdapter:
	"""
	IPA Connection adapter class
	"""

	def __init__(self, args: argparse.Namespace, notifier: EmailNotifier):
		try:
			process = subprocess.Popen(
				f"/usr/bin/kinit {args.principal} -k -t {args.keytab}".split(), stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			)
			if process.returncode is not None and process.returncode != 0:
				logging.error("Cannot obtain kerberos ticket")
				raise ValueError("Cannot obtain kerberos ticket")
		except ValueError:
			raise ValueError("Cannot obtain kerberos ticket")

		self._client = ClientMeta(args.server, verify_ssl=args.verify_ssl)
		try:
			self._client.login_kerberos()
		except Unauthorized as err:
			logging.error("login denied: %s", err)
			raise ValueError("login denied: %s" % err)

		self.admin_mail = args.admin
		self.limit_day = args.limit

		self.check_expiration = args.check_expiration
		self.check_locked = args.check_locked
		self.noop = args.noop

		self.notifier = notifier

	def __del__(self):
		self._client.logout()
		logging.debug("client logged out")
		subprocess.call(["/bin/kdestroy", "-A"])
		logging.debug("ticket is destroyed")

	def process_group(self, group: str) -> None:
		"""
		Process a single ldap group
		:param group: group name
		"""
		try:
			group_info = self._client.group_show(group)
		except NotFound:
			logging.error("no group named %s", group)
			return

		if self.check_expiration:
			self._check_password_expired(group_info['result']['member_user'])
		if self.check_locked:
			self._check_locked_users(group_info['result']['member_user'])

	def _check_password_expired(self, users: list) -> None:
		"""
		Check password expirations for given user list
		:param users: user uid list
		"""
		for username in users:
			user = self._client.user_show(username, all=True)['result']
			lock_status = user['nsaccountlock']
			if lock_status:
				continue

			email = user['mail'][0]
			password_expire_date = user['krbpasswordexpiration'][0]['__datetime__']
			password_expire_date = datetime.datetime.strptime(password_expire_date, '%Y%m%d%H%M%SZ')
			left_days = (password_expire_date - datetime.datetime.now()).days
			if left_days <= self.limit_day:
				logging.info("user %s expiration day left %d", user['uid'][0], left_days)
				if not self.noop:
					self.notifier.notify_expiration(email, password_expire_date, left_days)

	def _check_locked_users(self, users: list) -> None:
		"""
		Check lock status of given users
		:param users: user uid list
		"""
		locked_users = []
		for username in users:
			try:
				pw_policy = self._client.pwpolicy_show(user=username)
				user_status = self._client.user_status(username, all=True)
			except NotFound as err:
				logging.error("password policy find error: %s", err)
				continue

			if user_status['summary'].endswith("True"):
				continue

			blocked_servers = []
			for result in user_status['result']:
				server = result['server']
				is_failed = int(result['krbloginfailedcount'][0]) >= int(
					pw_policy['result']['krbpwdmaxfailure'][0])
				if is_failed:
					blocked_servers.append(server)
					logging.debug("account locked for %s in server %s", username, server)
			if len(blocked_servers) != 0:
				locked_users.append({'uid': username, 'servers': ', '.join(blocked_servers)})

		if len(locked_users) != 0:
			logging.info("locked users: %s", locked_users)
			if not self.noop:
				self.notifier.notify_locked_users(self.admin_mail, locked_users)
