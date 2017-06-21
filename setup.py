from setuptools import setup

exec(open('wikitables/version.py').read())

setup(name='wikitables',
      version=version,
      packages=['wikitables'],
      description='Import tables from any Wikipedia article',
      author='Bradley Cicenas',
      author_email='bradley@vektor.nyc',
      url='https://github.com/bcicen/wikitables',
      install_requires=['mwparserfromhell>=0.4.3', 'requests>=2.9.1'],
      license='http://opensource.org/licenses/MIT',
      classifiers=(
          'Natural Language :: English',
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'License :: OSI Approved :: MIT License',
      ),
      keywords='wikipedia data cli commandline',
      entry_points={ 'console_scripts': ['wikitables = wikitables.cli:main'] }
)
