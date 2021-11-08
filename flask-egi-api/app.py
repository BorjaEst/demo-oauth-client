from flask import Flask, url_for, session
from flask import render_template, redirect
from authlib.integrations.flask_client import OAuth
from authlib.integrations.flask_oauth2 import ResourceProtector, current_token
from authlib.oauth2.rfc6750 import BearerTokenValidator


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
    userinfo = oauth.egi.userinfo()
    if userinfo:
        session['user'] = userinfo
    return redirect('/')


class MyBearerTokenValidator(BearerTokenValidator):
    def authenticate_token(self, token_string):
        return function_to_return_token(token_string)

    def request_invalid(self, request):
        return False

    def token_revoked(self, token):
        return token.revoked


# only bearer token is supported currently
require_oauth = ResourceProtector()
require_oauth.register_token_validator(MyBearerTokenValidator())


@app.route('/resource')
@require_oauth('email')
def resource():
    # if Token model has `.user` foreign key
    # user = current_token.user
    return 'OK'
