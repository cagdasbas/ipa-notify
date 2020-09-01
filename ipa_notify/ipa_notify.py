import argparse
import datetime
import logging
import os
import subprocess
import sys

import requests
from python_freeipa import Client
from python_freeipa.exceptions import NotFound, Unauthorized
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from ipa_notify.notifier import Notifier

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def parse_args():
	parser = argparse.ArgumentParser(description='IPA Notifier')

	parser.add_argument('--server', type=str, default='ipa.domain.com', help='ipa server fqdn')
	parser.add_argument('--verify-ssl', dest='verify_ssl', action='store_true',
	                    help='verify ipa connection SSL cert (default)')
	parser.add_argument('--no-verify-ssl', dest='verify_ssl', action='store_false',
	                    help='do not verify ipa connection SSL cert')
	parser.set_defaults(verify_ssl=True)

	parser.add_argument('--principal', type=str, default='admin@DOMAIN.COM',
	                    help='user principal for kerberos authentication')
	parser.add_argument('--keytab', type=str, default='/tmp/user.kt', help='keytab path')

	parser.add_argument('--groups', nargs='+', type=str, default=['users'], help='list of user groups to check')
	parser.add_argument('--limit', type=int, default=5, help='number of days before notifying a user')

	parser.add_argument('--smtp-host', dest='smtp_host', type=str, default='localhost',
	                    help='smtp host for sending email')
	parser.add_argument('--smtp-port', dest='smtp_port', type=int, default=587,
	                    help='smtp port for sending email')
	parser.add_argument('--smtp-user', dest='smtp_user', type=str, default='smtp_user',
	                    help='smtp user login')
	parser.add_argument('--smtp-pass', dest='smtp_pass', type=str, default='smtp_pass',
	                    help='smtp user password')
	parser.add_argument('--smtp-from', dest='smtp_from', type=str, default='noreply@domain.com',
	                    help='smtp from email address')

	parser.add_argument('--admin', type=str, default='admin@domain.com',
	                    help='admin user email to notify about locked users')
	parser.add_argument('--noop', type=bool, default=False, help='no operation mode. Do not send emails')

	parser.add_argument('--loglevel', dest='log_level', type=str, choices=list(logging._levelToName.values()),
	                    default='INFO',
	                    help='log level')

	args = parser.parse_args()
	return args


def main():
	args = parse_args()
	logging.basicConfig(
		format='%(asctime)s - %(module)s.%(funcName)s - %(levelname)s - %(message)s',
		level=getattr(logging, args.log_level, None)
	)

	admin_mail = args.admin
	limit_day = args.limit

	locked_users = []

	if not os.path.exists(args.keytab):
		logging.error("Please obtain a keytab file with following command:")
		logging.error("ipa-getkeytab -s ipa.domain.com -p admin@DOMAIN.COM -P -k ~/.priv/admin.kt")
		sys.exit(2)

	subprocess.call(f"/usr/bin/kinit {args.principal} -k -t {args.keytab}".split())

	client = Client(args.server, version='2.215', verify_ssl=args.verify_ssl)
	try:
		client.login_kerberos()
	except Unauthorized as e:
		logging.error(f"login denied: {str(e)}")
		sys.exit(1)

	notifier = Notifier(host=args.smtp_host, port=args.smtp_port, user=args.smtp_user, password=args.smtp_pass,
	                    from_email=args.smtp_from)

	for group in args.groups:
		try:
			group_info = client.group_show(group)
		except NotFound as e:
			logging.error(f"no group named {group}")
			continue

		for user in group_info['member_user']:
			user = client.user_show(user)
			lock_status = user['nsaccountlock']
			if lock_status:
				locked_users.append(user)

			email = user['mail'][0]
			password_expire_date = user['krbpasswordexpiration'][0]['__datetime__']
			password_expire_date = datetime.datetime.strptime(password_expire_date, '%Y%m%d%H%M%SZ')
			left_days = (password_expire_date - datetime.datetime.now()).days
			if left_days <= limit_day:
				logging.info(f"user {user['uid'][0]} expiration day left {left_days}")
				if not args.noop:
					notifier.notify_expiration(email, password_expire_date, left_days)

	if len(locked_users) != 0:
		logging.info(f"locked users: {','.join(locked_users)}")
		if not args.noop:
			notifier.notify_locked_users(admin_mail, locked_users)


if __name__ == '__main__':
	main()
