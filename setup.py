import os

from setuptools import setup, find_packages

from ipa_notify.release import __version__


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
	version=__version__,
	url='https://github.com/cagdasbas/ipa-notify',
	python_requires='>=3.6',
	description='FreeIPA password expriation and locked user notifier',
	long_description=read_file('README.md'),
	long_description_content_type="text/markdown",
	author='Cagdas Bas',
	author_email='cagdasbs@gmail.com',
	packages=find_packages("."),
	include_package_data=True,
	entry_points={
		"console_scripts": [
			"ipa-notify = ipa_notify.__main__:main",
		]
	},
	install_requires=read_requirements('requirements.txt'),
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'License :: OSI Approved :: Apple Public Source License',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.8',
		'Programming Language :: Python :: 3.9',
	],
)
