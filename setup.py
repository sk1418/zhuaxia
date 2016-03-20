from setuptools import setup, find_packages
import glob
import zhuaxia.zxver as zxver
setup(
    name = 'zhuaxia',
    version = zxver.version,
    install_requires=['pycrypto', 'requests','mutagen','beautifulsoup4' ],
    packages = find_packages(),
    package_data={'zhuaxia':['conf/default.*']},
    #data_files=[('conf',glob.glob('conf/*.*'))],
    include_package_data= True,
    zip_safe=False,
    scripts=['zx'],
    author='Kai Yuan',
    author_email='kent.yuan@gmail.com',
    platforms=['POSIX'],
    keywords='xiami mp3 download',
    url='https://github.com/sk1418/zhuaxia',
    description='a cli tool to download mp3 from xiami.com and music.163',
    long_description="""
        a cli tool to download mp3 from xiami.com and music.163  
    """,
)
