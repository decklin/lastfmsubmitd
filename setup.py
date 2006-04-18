#!/usr/bin/python

from distutils.core import setup

setup(
    name='lastfmsubmitd',
    version='0.28',
    description='Last.fm submit daemon and example MPD/MusicBrainz clients',
    author='Decklin Foster',
    author_email='decklin@red-bean.com',
    url='http://www.red-bean.com/~decklin/software/lastfmsubmitd/',
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Development Status :: 4 - Beta',
        'License :: MIT/X Consortium License',
        'Topic :: Multimedia :: Sound :: Players',
        'Operating System :: POSIX',
        'Environment :: No Input/Output (Daemon)',
        'Programming Language :: Python',
        ],
    package_dir = {'': 'lib'},
    packages = ['lastfm'],
    scripts = [
        'lastfmsubmitd',
        'lastmp',
        'lastcd',
        'mbfind',
        'mbget',
        'mbsubmit',
        ],
    data_files=[
        ('share/man/man1', [
            'doc/lastfmsubmitd.1',
            'doc/lastmp.1',
            'doc/mbget.1',
            ]),
        ('lib/lastfmsubmitd', [
            'lastfmsubmit',
            ]),
        ],
    )
