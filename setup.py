from distutils.core import setup

from bearlib import __version__, __author__, __contact__, __license__, __doc__

setup(name='bearlib',
      version=__version__,
      author=__author__,
      author_email=__contact__,
      packages=['bearlib', ],
      url='http://pypi.python.org/pypi/bearlib/',
      license=__license__,
      description=__doc__,
      long_description=open('README').read(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
     )
