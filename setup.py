from distutils.core import setup

setup(
	name='tabularpy',
	version='1.0',
	description='Python tablular information manupulation library',
	author='Anthony Post',
	author_email='postanthony3000@gmail.com',
	url='https://github.com/Ayehavgunne/tabularpy/',
	packages=['tabularpy'],
	extras_require={'Parsing Date/time strings': ['dateutil'], 'Parsing complex HTML': ['BeautifulSoup4']}
)
