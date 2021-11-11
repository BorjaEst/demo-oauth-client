import requests
from authlib.integrations.flask_client import OAuth
from authlib.integrations.flask_oauth2 import ResourceProtector, current_token
from authlib.oauth2.rfc7662 import IntrospectTokenValidator
from flask import Flask, redirect, render_template, session, url_for


app = Flask(__name__)
app.secret_key = '!secret'
app.config.from_object('config')

CONF_URL = 'https://aai-dev.egi.eu/oidc/.well-known/openid-configuration'
oauth = OAuth(app)
oauth.register(
    name='egi',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)


@app.route('/')
def homepage():
    user = session.get('user')
    return render_template('home.html', user=user)


@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.egi.authorize_redirect(redirect_uri)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


@app.route('/auth')
def auth():  # GET /auth?code=<authorization_code>&state=<state_value.>
    token = oauth.egi.authorize_access_token()
    return token['access_token']


class MyIntrospectTokenValidator(IntrospectTokenValidator):
    def introspect_token(self, token_string):
        oauth.egi.load_server_metadata()
        url = oauth.egi.server_metadata['introspection_endpoint']
        data = {'token': token_string, 'token_type_hint': 'access_token'}
        auth = (oauth.egi.client_id, oauth.egi.client_secret)
        resp = requests.post(url, data=data, auth=auth)
        resp.raise_for_status()
        return resp.json()


# only bearer token is supported currently
require_oauth = ResourceProtector()
require_oauth.register_token_validator(MyIntrospectTokenValidator())


@app.route('/resource')
@require_oauth('email')
def resource():
    # if Token model has `.user` foreign key
    # user = current_token.user
    return 'OK'
