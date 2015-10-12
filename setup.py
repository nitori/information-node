
import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import shutil
import sys
import textwrap

def require_py33():
    # make sure this is only installed on Python 3.3 or later:
    if sys.version_info[0] < 3 or sys.version_info[1] < 3:
        sys.stderr.write("Sorry, Python < 3.3 is not supported\n")
        sys.exit(1)
#require_py33()

# import requirements.txt for info:
with open(os.path.join(os.path.dirname(__file__), "requirements.txt")) as f:
    required = [l for l in f.read().splitlines() if not l.startswith("#")\
        and len(l.strip()) > 0]

# helper from tox documentation to run tox for testing:
class Tox(TestCommand):
    # add custom options for tox:
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex

        # get tox arguments from user options:
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)

        # launch tox and exit with return code:
        errno = tox.cmdline(args=args)
        sys.exit(errno)

# create informationnode.data for package-included data, and put LICENSE.txt
# and AUTHORS.md in there:
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
    license = "GPLv2+",
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
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Communications",
        "Topic :: System :: Archiving",
    ],
    tests_require=["tox"],
    zip_safe=False,
    cmdclass={'test': Tox},
)


