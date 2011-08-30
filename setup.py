from setuptools import setup, find_packages

setup(
    name = "SoundCloud API",
    version = "0.1",
    packages = find_packages(),
    author = "Hans Kuder",
    author_email = "hanskuder@gmail.com"
    description = "SoundCloud REST API with support for OAuth2. Adapted from older: http://github.com/soundcloud/python-api-wrapper",
    license = "MIT",
    keywords = "Soundcloud client API REST oauth2",
    url = "http://github.com/hiidef/soundcloud-python",
    install_requires = ['simplejson']
)

