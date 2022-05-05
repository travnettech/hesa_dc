from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in hesa_dc/__init__.py
from hesa_dc import __version__ as version

setup(
	name="hesa_dc",
	version=version,
	description="HESA Data Collection",
	author="Sitenet Tech",
	author_email="info@sitenet.tech",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
