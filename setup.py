from setuptools import setup, find_packages

import os


def main():

    def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

    setup(
        name='tangods-moco',
        packages= find_packages(),
        version = '1.3.0',    
        url = "http://www.maxiv.lu.se",
        author='Juliano Murari',
        author_email='juliano.murari@maxiv.lu.se',
        description='This package contains Tango Device for MoCo equipment',
        platforms = "all",        
        include_package_data = True,
    
   	# Define automatic scripts tht will be created during installation.
	entry_points={
	   'console_scripts': [
	       'Moco = PyMocoDS.Moco:main',
	   ],
	}
	)


if __name__ == "__main__":
    main()
