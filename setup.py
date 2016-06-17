from setuptools import setup

exec(open('wikitables/version.py').read())

setup(name='wikitables',
      version=version,
      packages=['wikitables'],
      description='Import any Wikipedia table as a dataset',
      author='Bradley Cicenas',
      author_email='bradley.cicenas@gmail.com',
      url='https://github.com/bcicen/wikitables',
      install_requires=['mwparserfromhell>=0.4.3', 'requests>=2.9.1'],
      license='http://opensource.org/licenses/MIT',
      classifiers=(
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License ',
          'Natural Language :: English',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
      ),
      keywords='wikipedia data',
)
