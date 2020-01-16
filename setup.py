from setuptools import setup, find_packages

setup(
    name='mailupy',
    version='0.0.0',
    url='',
    install_requires=[],
    description="Yet another Mailup Python client",
    long_description=open('README.rst', 'r').read(),
    license="MIT",
    author="Lotrèk",
    author_email="dimmitutto@lotrek.it",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ]
)
