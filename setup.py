
import os
from setuptools import setup, find_packages
import shutil
import textwrap

with open("requirements.txt") as f:
    required = [l for l in f.read().splitlines() if not l.startswith("#")\
        and len(l.strip()) > 0]

if not os.path.exists(os.path.join(os.path.dirname(__file__),
        "informationnode", "data")):
    os.mkdir(os.path.join(os.path.dirname(__file__), "informationnode",
        "data"))
for data_file in [ "AUTHORS.md", "LICENSE.txt" ]:
    shutil.copyfile(os.path.join(os.path.dirname(__file__), data_file),
        os.path.join(os.path.dirname(__file__), "informationnode", "data",
        data_file))
setup(
    name = "information-node",
    version = "0.1",
    author = "Information Node Development Team",
    description = textwrap.dedent('''\
        A data synchronization software which syncs data between nodes,
        supports basic files and special data like messages (e-mails, ...)
        and syncing to IMAP/messengers/.., and which supports encryption.'''),
    license = "GPLv3+",
    keywords = "node cloud data synchronization",
    url = "https://github.com/information-node/information-node",
    packages=["informationnode"] + [os.path.join("informationnode", p) \
        for p in find_packages('informationnode')],
    package_data={"informationnode" : ['data/*']},
    scripts=['information-node', 'inode-viewer', 'inode-viewer-cli'],
    install_requires=required,
    long_description=open(os.path.join(os.path.dirname(__file__),
        'README.md'), "r").read(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Communications",
        "Topic :: System :: Archiving",
    ],
    zip_safe=False,
)


