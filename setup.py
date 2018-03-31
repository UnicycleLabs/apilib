from setuptools import setup, find_packages

setup(
    name='apilib',
    description='A library for defining APIs that will serialize into JSON.',
    author='Jonathan Goldman',
    author_email='jonathan@unicyclelabs.com',
    url='https://github.com/UnicycleLabs/apilib',
    version='0.3.0',
    packages=find_packages(),
    install_requires=['six', 'python-dateutil', 'requests'],
    extras_require={'encrypted-ids': ['hashids']},
    tests_require=['mock'],
    test_suite='tests.all_tests')
