from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='quantify',
    version='0.0.0',
    description='An application to design, test and run quantitative strategies',
    long_description_content_type="text/markdown",
    long_description=README + '\n',
    license='Proprietary',
    packages=find_packages(),
    author='Green Planet Capital',
    author_email='greenplanetcap.unofficial@gmail.com',
    keywords=['GPC', 'GreenPlanetCapital'],
    url='https://github.com/GreenPlanet-Capital/Quantify',
    download_url='https://github.com/GreenPlanet-Capital/Quantify',
    include_package_data=True,
    entry_points={
        'console_scripts': ['quantify=Quantify.app_f.shell:main']
    },
)

install_requires = [
    'setuptools',
    'wheel',
    'DataManager @ git+https://github.com/GreenPlanet-Capital/DataManager@install_b',
    'matplotlib',
    'tqdm',
    'prettytable',
    'plotly',
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)