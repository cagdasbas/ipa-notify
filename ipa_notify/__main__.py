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
import os
import sys

import requests
from jinja2 import Environment, PackageLoader, ChoiceLoader, FileSystemLoader
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from ipa_notify import parse_args
from ipa_notify.email_notifier import EmailNotifier
from ipa_notify.ipa_adapter import IPAAdapter

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def init_logging(level):
	"""
	Initialize logging
	:param level: log level
	"""
	logging.basicConfig(
		format='%(asctime)s - %(module)s.%(funcName)s - %(levelname)s - %(message)s',
		level=getattr(logging, level, None)
	)


def init(args: argparse.Namespace) -> IPAAdapter:
	"""
	Initialize application
	:param args: command line arguments
	:return: (ipa_client, email_notifier)
	"""

	if not os.path.exists(args.keytab):
		logging.error("Cannot find keytab file %s", args.keytab)
		sys.exit(2)

	loaders = []
	if args.templates != '':
		if os.path.isdir(args.templates):
			loaders.append(FileSystemLoader(args.templates))
		else:
			logging.error("Given path for templates is not a folder, continuing with default templates")

	loaders.append(PackageLoader('ipa_notify', 'templates'))
	template_env = Environment(
		loader=ChoiceLoader(loaders)
	)

	notifier = EmailNotifier(
		host=args.smtp_host, port=args.smtp_port,
		user=args.smtp_user, password=args.smtp_pass,
		from_email=args.smtp_from,
		template_env=template_env
	)

	try:
		ipa_adapter = IPAAdapter(args, notifier)
	except ValueError as err:
		logging.error("Error creating IPA Adapter: %s", err)
		sys.exit(5)
	return ipa_adapter


# pylint: disable=too-many-locals
def main():
	"""
	Main application process.
	Checks each user in given groups for password expiration
	"""

	args = parse_args()
	init_logging(args.log_level)

	if not args.check_expiration and not args.check_locked:
		logging.error("You should at least enable one check")
		sys.exit(4)

	ipa_adapter = init(args)

	for group in args.groups:
		ipa_adapter.process_group(group)


if __name__ == '__main__':
	main()
