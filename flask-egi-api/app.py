from flask import Flask, url_for, session
from flask import render_template, redirect
from authlib.integrations.flask_client import OAuth


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


@app.route('/auth')
def auth(): # GET /auth?code=<authorization_code>&state=<state_value.>
    token = oauth.egi.authorize_access_token()
    userinfo = oauth.egi.userinfo()
    if userinfo:
        session['user'] = userinfo
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


# @app.route('/resource')
# def resource():

#     user = token.get('userinfo')
#     if user:
#         session['user'] = user
#     return redirect('/')
