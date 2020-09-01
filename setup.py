import os

from setuptools import setup, find_packages


def read_file(file_name):
	"""Read file and return its contents."""
	with open(file_name, 'r') as f:
		return f.read()


def read_requirements(file_name):
	"""Read requirements file as a list."""
	print(os.listdir('.'))
	reqs = read_file(file_name).splitlines()
	if not reqs:
		raise RuntimeError(
			"Unable to read requirements from the %s file"
			"That indicates this copy of the source code is incomplete."
			% file_name
		)
	return reqs


setup(
	name='ipa-notify',
	version='0.1',
	description='FreeIPA password expriation and locked user notifier',
	author='Cagdas Bas',
	author_email='cagdasbs@gmail.com',
	packages=find_packages("."),
	include_package_data=True,
	entry_points={
		"console_scripts": [
			"ipa-notify = ipa_notify.ipa_notify:main",
		]
	},
	install_requires=read_requirements('requirements.txt')
)
