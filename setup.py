from setuptools import setup, find_packages

import os


def main():

    def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    with open('PyMocoDS/VERSION') as f:
        version = f.readline().strip()

    setup(
        name='MocoDS',
        packages= find_packages(),
        version = version,    
        long_description=read('README.md'),
        scripts=[],
        data_files=[],
        url='http://www.cells.es',
        author='CTBeamlines',
        author_email='ctbeamlines@cells.es',
        description='This package contains MoCo DS'
        platforms = "all",        
        include_package_data = True,
    )
    
    # Define automatic scripts tht will be created during installation.
    entry_points={
        'console_scripts': [
            'Moco = PyMocoDS.Moco:main',
        ],
    }



if __name__ == "__main__":
    main()
