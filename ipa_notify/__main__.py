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
import os
import subprocess
import sys

import requests
from python_freeipa.client_meta import ClientMeta
from python_freeipa.exceptions import NotFound, Unauthorized
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from ipa_notify import parse_args
from ipa_notify.notifier import Notifier

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def init(args: argparse.Namespace) -> tuple:
	"""
	Initialize application
	:param args: command line arguments
	:return: (ipa_client, email_notifier)
	"""
	logging.basicConfig(
		format='%(asctime)s - %(module)s.%(funcName)s - %(levelname)s - %(message)s',
		level=getattr(logging, args.log_level, None)
	)

	if not os.path.exists(args.keytab):
		logging.error("Cannot find keytab file %s", args.keytab)
		sys.exit(2)

	try:
		process = subprocess.Popen(
			f"/usr/bin/kinit {args.principal} -k -t {args.keytab}".split(), stdout=subprocess.PIPE,
			stderr=subprocess.PIPE
		)
		if process.returncode is not None and process.returncode != 0:
			logging.error("Cannot obtain kerberos ticket")
			sys.exit(3)
	except ValueError:
		sys.exit(3)

	client = ClientMeta(args.server, verify_ssl=args.verify_ssl)
	try:
		client.login_kerberos()
	except Unauthorized as err:
		logging.error("login denied: %s", err)
		sys.exit(1)

	notifier = Notifier(
		host=args.smtp_host, port=args.smtp_port,
		user=args.smtp_user, password=args.smtp_pass,
		from_email=args.smtp_from
	)
	return client, notifier


# pylint: disable=too-many-locals
def main():
	"""
	Main application process.
	Checks each user in given groups for password expiration
	"""

	args = parse_args()
	ipa_client, email_notifier = init(args)

	admin_mail = args.admin
	limit_day = args.limit

	locked_users = []
	for group in args.groups:
		try:
			group_info = ipa_client.group_show(group)
		except NotFound:
			logging.error("no group named %s", group)
			continue

		for username in group_info['result']['member_user']:
			user = ipa_client.user_show(username, all=True)['result']
			lock_status = user['nsaccountlock']
			if lock_status:
				continue

			try:
				pw_policy = ipa_client.pwpolicy_show(user=username)
				user_status = ipa_client.user_status(username, all=True)
				if int(user_status['result'][0]['krbloginfailedcount'][0]) >= \
						int(pw_policy['result']['krbpwdmaxfailure'][0]):
					logging.debug("account locked for %s", username)
					locked_users.append(username)
			except NotFound as err:
				logging.error("password policy find error: %s", err)

			email = user['mail'][0]
			password_expire_date = user['krbpasswordexpiration'][0]['__datetime__']
			password_expire_date = datetime.datetime.strptime(password_expire_date, '%Y%m%d%H%M%SZ')
			left_days = (password_expire_date - datetime.datetime.now()).days
			if left_days <= limit_day:
				logging.info("user %s expiration day left %d", user['uid'][0], left_days)
				if not args.noop:
					email_notifier.notify_expiration(email, password_expire_date, left_days)

	if len(locked_users) != 0:
		logging.info("locked users: %s", locked_users)
		if not args.noop:
			email_notifier.notify_locked_users(admin_mail, locked_users)

	subprocess.call(["/bin/kdestroy", "-A"])


if __name__ == '__main__':
	main()
