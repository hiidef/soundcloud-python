from soundcloud import fetch_access_token, ApiConnector, Scope
import sys
import urllib2

client_id = "a50b2a1f4dc7167b934baa432701f0c0"
client_secret = "fae3d6fd5b77177834dffeed8d073452"
redirect_uri = "http://goodsietest.com:8000/soundcloud/oauth_redirect"
token_url = "https://api.soundcloud.com/oauth2/token"

#code = sys.argv[1]

#token = fetch_access_token(token_url, client_id, client_secret, redirect_uri, code)
token = sys.argv[1]

connector = ApiConnector("api.soundcloud.com", token)
scope = Scope(connector)

download_url = scope.me().tracks().next().get_temporary_download_url(token)

print download_url
