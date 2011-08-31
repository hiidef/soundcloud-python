from textwrap import dedent
import os
from configobj import ConfigObj
from validate import Validator
import webbrowser
import soundcloud

config = {
        'CONFIG_NAME': "test.ini",
        'CLIENT_ID': None,
        'CLIENT_SECRET': None,
        'TOKEN_URI': None,
        'REDIRECT_URI': None,
        'API_HOST': None
}

CONFIGSPEC=dedent("""
[api]
api_host=string(default=api.soundcloud.com)
client_id=string
client_secret=string
token_uri=string
redirect_uri=string

[proxy]
use_proxy=boolean(default=false)
proxy=string(default=http://127.0.0.1:10000/)

[logging]
test_logger=string(default=ERROR)
api_logger=string(default=ERROR)

[test]
run_interactive_tests=boolean(default=false)
""")


def load_config():
    """
    Loads the configuration by looking from

     - the environment variable soundcloud_CONFIG
     - the installation location upwards until it finds test.ini
     - the current working directory upwards until it finds test.ini

    Raises an error if there is no config found
    """
    config_name = config['CONFIG_NAME']

    name = None

    if "soundcloud_CONFIG" in os.environ:
        if os.path.exists(os.environ["soundcloud_CONFIG"]):
            name = os.environ["soundcloud_CONFIG"]

    def search_for_config(current):
        while current:
            name = os.path.join(current, config_name)
            if os.path.exists(name):
                return name
            new_current = os.path.dirname(current)
            if new_current == current:
                return
            current = new_current

    if name is None:
        name = search_for_config(os.path.dirname(__file__))
    if name is None:
        name = search_for_config(os.getcwd())

    if not name:
        raise Exception("No test configuration file found!")

    parser = ConfigObj(name, configspec=CONFIGSPEC.split("\n"))
    val = Validator()
    if not parser.validate(val):
        raise Exception("Config file validation error")

    api = parser['api']
    config['API_HOST'] = api.get('api_host')
    config['CLIENT_ID'] = api.get('client_id')
    config['CLIENT_SECRET'] = api.get('client_secret')
    config['TOKEN_URI'] = api.get('token_uri')
    config['REDIRECT_URI'] = api.get('redirect_uri')

load_config()

authenticator = soundcloud.OAuth2Authenticator( config['CLIENT_ID'], 
                                                config['CLIENT_SECRET'],
                                                config['REDIRECT_URI'])

connect_url = authenticator.construct_connect_url()

webbrowser.open(connect_url)
authorization_code = raw_input("After connecting, please enter the code parameter in the browser's address bar (code=...): ")

authenticator = soundcloud.OAuth2Authenticator( config['CLIENT_ID'], 
                                                config['CLIENT_SECRET'],
                                                config['REDIRECT_URI'],
                                                None,
                                                authorization_code)

token = authenticator.fetch_access_token()

print "Done! Make sure to add this line to your test.ini under [api]:"
print "access_token=%s" % token
