# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from aldryn_forms import __version__

REQUIREMENTS = [
    'aldryn-boilerplates>=0.7.5',
    'django-cms>=3.2',
    'django-emailit',
    'djangocms-text-ckeditor',
    'djangocms-attributes-field>=0.3.0',
    'django-simple-captcha',
    'django-recaptcha2',
    'django-recaptcha3',
    'django-turnstile',
    'tablib',
    'pillow',
    'django-filer',
    'django-sizefield',
    'Django>=1.8',
    'openpyxl',  # 2.5.0b1 is raising "ImportError: cannot import name '__version__'"
    'six>=1.0',
    'html2text',
]

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Framework :: Django :: 1.8',
    'Framework :: Django :: 1.9',
    'Framework :: Django :: 1.10',
    'Framework :: Django :: 1.11',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]

setup(
    name='js-forms',
    version=__version__,
    description='Create forms and embed them on CMS pages',
    author='Divio AG',
    author_email='info@divio.ch',
    url='https://github.com/aldryn/aldryn-forms',
    packages=find_packages(),
    license='LICENSE.txt',
    platforms=['OS Independent'],
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    include_package_data=True,
    zip_safe=False,
    test_suite='tests.settings.run',
)
