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
import logging


def parse_args() -> argparse.Namespace:
	"""
	Parse cmdline arguments
	:return: arguments
	"""
	parser = argparse.ArgumentParser(
		"ipa-notify",
		description="IPA Notifier",
		formatter_class=argparse.ArgumentDefaultsHelpFormatter
	)

	parser.add_argument('--server', type=str, default='ipa.domain.com', help='ipa server fqdn')
	parser.add_argument('--verify-ssl', dest='verify_ssl', action='store_true',
	                    help='verify ipa connection SSL cert (default)')
	parser.add_argument('--no-verify-ssl', dest='verify_ssl', action='store_false',
	                    help='do not verify ipa connection SSL cert')
	parser.set_defaults(verify_ssl=True)

	parser.add_argument('--principal', type=str, default='admin@DOMAIN.COM',
	                    help='user principal for kerberos authentication')
	parser.add_argument('--keytab', type=str, default='/tmp/user.kt', help='keytab path')

	parser.add_argument('--groups', nargs='+', type=str, default=['users'],
	                    help='list of user groups to check')
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
	parser.add_argument('--noop', type=bool, default=False,
	                    help='no operation mode. Do not send emails')

	parser.add_argument('--loglevel', dest='log_level', type=str,
	                    choices=list(logging._nameToLevel.keys()), default='INFO',
	                    help='log level')

	args = parser.parse_args()
	return args
