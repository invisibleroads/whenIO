import os
from setuptools import setup, find_packages


HERE = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(HERE, 'README.rst')).read()
CHANGES = open(os.path.join(HERE, 'CHANGES.rst')).read()


setup(
    name='whenIO',
    version='1.5.2',
    description='Methods for formatting and parsing friendly timestamps',
    long_description=README + '\n\n' + CHANGES,
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='datetime time',
    author='Roy Hyunjin Han',
    author_email='starsareblueandfaraway@gmail.com',
    url='https://github.com/invisibleroads/whenIO',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'python-dateutil',
        'pytz',
        'tzlocal',
    ],
    test_suite='whenIO.tests',
    tests_require=['nose'],
    zip_safe=True)
