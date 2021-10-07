from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in load_controls/__init__.py
from load_controls import __version__ as version

setup(
	name='load_controls',
	version=version,
	description='Load Controls',
	author='jan',
	author_email='janlloydangeles@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
