from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name='spotifyy',
    version='0.1.0',
    description='Spotify interface used for Spotbot',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    packages=find_packages(),
    author='Saltpile123',
    author_email='',
    keywords=['spotify', 'aiml', 'spotbot', 'spotifyy'],
    url='https://github.com/JesperK123456/spotifyy',
    download_url='https://pypi.org/project/spotifyy/'
)

install_requires = [
    'spotipy>=2.10.0',
    'programy>=4.1.5'
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)