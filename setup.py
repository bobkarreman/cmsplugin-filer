import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "cmsplugin-filer",
    version = "0.9.4",
    url = 'http://github.com/stefanfoulis/cmsplugin-filer',
    license = 'BSD',
    description = "django-cms plugins for django-filer",
    long_description = read('README.rst'),
    author = 'Stefan Foulis',
    author_email = 'stefan.foulis@gmail.com',
    packages = find_packages(),
    #package_dir = {'':'src'},
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    install_requires=[
        "Django >= 1.3",
        "django-cms >= 2.2",
        "django-sekizai >= 0.4.2",
        "easy_thumbnails >= 1.0",
        "django-filer >= 0.9"
    ],
    include_package_data=True,
    zip_safe = False,
)
