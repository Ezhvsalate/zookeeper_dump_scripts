from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='zoodumper',
    version='0.1',
    author="ezhvsalate",
    author_email="ezhvsalate@ya.ru",
    description="Small utility to make a dump of zookeeper tree and store it on other host",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ezhvsalate/zookeeper_dump_scripts",
    py_modules=['zoodumper'],
    python_requires=">=3.6",
    install_requires=[
        'Click',
        'Kazoo'
    ],
    entry_points='''
        [console_scripts]
        zoodumper=zoodumper:cli
    ''',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
