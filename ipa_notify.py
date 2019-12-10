import argparse
import datetime
import subprocess

from python_freeipa import Client
from python_freeipa.exceptions import NotFound

from helper import notify_expiration, notify_locked_users

parser = argparse.ArgumentParser(description='IPA Notifier')

parser.add_argument('--server', type=str, default='ipa.domain.com', help='ipa server fqdn')
parser.add_argument('--verify-ssl', dest='verify_ssl', action='store_true',
                    help='verify ipa connection SSL cert (default)')
parser.add_argument('--no-verify-ssl', dest='verify_ssl', action='store_false',
                    help='do not verify ipa connection SSL cert')
parser.set_defaults(verify_ssl=True)

parser.add_argument('--admin', type=str, default='admin@domain.com',
                    help='admin user email to notify about locked users')
parser.add_argument('--keytab', type=str, default='/tmp/user.kt', help='keytab path')

parser.add_argument('--groups', nargs='+', type=str, default=['users'], help='list of user groups to check')

parser.add_argument('--limit', type=int, default=5, help='number of days before notifying a user')
parser.add_argument('--noop', type=bool, default=False, help='no operation mode. Do not send emails')
args = parser.parse_args()

admin_mail = args.admin
limit_day = args.limit

locked_users = []

subprocess.call(('/usr/bin/kinit %s -k -t %s' % (args.admin, args.keytab)).split())

client = Client(args.server, version='2.215', verify_ssl=args.verify_ssl)
client.login_kerberos()
for group in args.groups:
	try:
		group_info = client.group_show(group)
	except NotFound as e:
		print('no group named "%s"' % group)
		continue

	for user in group_info['member_user']:
		user = client.user_show(user)
		lock_status = user['nsaccountlock']
		if lock_status:
			if not args.noop:
				locked_users.append(user)
			else:
				print('user is locked %s' % user['uid'][0])

		email = user['mail'][0]
		password_expire_date = user['krbpasswordexpiration'][0]['__datetime__']
		password_expire_date = datetime.datetime.strptime(password_expire_date, '%Y%m%d%H%M%SZ')
		left_days = (password_expire_date - datetime.datetime.now()).days
		if left_days <= limit_day:
			if not args.noop:
				notify_expiration(email, password_expire_date, left_days)
			else:
				print('user %s expiration day left %d ' % (user['uid'][0], left_days))

if len(locked_users) != 0:
	if not args.noop:
		notify_locked_users(admin_mail, locked_users)
	else:
		print('locked users: %s' % (','.join(locked_users)))
