"""
For setup example see end of http://www.sourceweaver.com/blog/view/private-python-egg-repository
http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
http://morepath.readthedocs.io/en/latest/organizing_your_project.html#namespace-packages
http://setuptools.readthedocs.io/en/latest/setuptools.html#namespace-packages
"""
from setuptools import setup, find_packages

setup(
	url="",
	zip_safe=False,
	name="dotmpe-du-ext",
	version="0.0.1",
	author="B. van Berkum",
	author_email="dev@dotmpe.com",
	description="",
	long_description="""
""",
	license="GPLv3",
	#test_suite=TestSuite,
	scripts=[
		#"scripts/<name>",
	],
	install_requires=[
		# 'cllct-core'
	],
	packages=find_packages('lib/py'),
	package_data={
            '': ['lib/py']
	},
	package_dir = {
	    'cllct': 'lib/py/cllct',
	    'dotmpe': 'lib/py/dotmpe',
	    'dotmpe.du.ext': 'lib/py/dotmpe/du/ext'
        },
	eager_resources = [
	],
	entry_points = {
		# console_scripts': [ '<script-name> = <package-name>.main:main' ]
	},
	namespace_packages = [
		'cllct',
		'dotmpe',
		'dotmpe.du.ext'
	]
)


