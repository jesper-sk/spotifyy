import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spotifyy", # Replace with your own username
    version="0.1.1",
    author="Saltpile123",
    author_email="ikhoudvanberichten@gmail.com",
    description="Spotify interface used by Spotbot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JesperK123456/spotifyy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.6',
)