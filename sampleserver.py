import psycopg2
import requests
from flask import Flask, redirect, render_template, request, url_for, session, make_response
from flask_login import login_required, login_user, LoginManager, logout_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import random
import os

app = Flask(__name__)

app.secret_key = os.urandom(24)

@app.before_request
def session_management():
    pass

@app.route('/')
def index():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    
    credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])

    client = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
  
    return channels_list_by_username(client, part='snippet,contentDetails,statistics',forUsername='GoogleDevelopers')


@app.route('/authorize')
def authorize():
  # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow
  # steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
      # This parameter enables offline access which gives your application
      # both an access and refresh token.
      # This parameter enables incremental auth.
  # Store the state in the session so that the callback can verify that
  # the authorization server response.
    flask.session['state'] = state
    return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verify the authorization server response.
    state = flask.session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

  # Store the credentials in the session.
  # ACTION ITEM for developers:
  #     Store user's access and refresh tokens in your data store if
  #     incorporating this code into your real app.
    credentials = flow.credentials
    flask.session['credentials'] = {'token': credentials.token,
      'refresh_token': credentials.refresh_token,
      'token_uri': credentials.token_uri,
      'client_id': credentials.client_id,
      'client_secret': credentials.client_secret,
      'scopes': credentials.scopes}
    return flask.redirect(flask.url_for('index'))

def channels_list_by_username(client, **kwargs):
    response = client.channels().list(**kwargs).execute()
    return flask.jsonify(**response)

###########################################

@app.route('/home')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return "Hello Boss!  <a href='/logout'>Logout</a>"
 
@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        return "wrong password!"
    return home()

@app.route('/setcookie', methods = ['POST', 'GET'])
def setcookie():
    if request.method == 'POST':
        user = request.form['username']
   
    resp = make_response(render_template('readcookie.html'))
    resp.set_cookie('userID', user)
    return resp

@app.route('/getcookie')
def getcookie():
   name = request.cookies.get('userID')
   return '<h1>welcome '+name+'</h1>'

 
@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()
 

@app.route('/pgdbquery/<dbname>/<name>')
def hello1(dbname, name):
    conn = psycopg2.connect(database='trainer', user='trainer1',
                            password='training', host='192.168.1.50',
                            port='5432')
    cur = conn.cursor()
    s = "SELECT * FROM " + dbname + " LIMIT 10000"
    cur.execute(s)
    colnames = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return render_template('hello.html', title=dbname, user=dbname,
                           name=name, rows=rows, dbname=dbname, colnames=colnames)


@app.route('/download/<path:path>')
def static_file(path):
    return app.send_static_file(path)


@app.route('/episode/<episode>')
def download_episode(episode):
    s1 = "http://fromv.ir/vip/Anime/Complete/Hunter%20x%20Hunter_2011/720/Hunter%20x%20Hunter_2011.%20"
    # episode = "002"
    s2 = ".720%20Blu-ray%5BFromAnime%5D"
    extension = ".mkv"
    file_prefix = "Hunter X Hunter"
    file_url = s1 + episode + s2 + extension

    r = requests.get(file_url, stream=True)
    with open(file_prefix + episode + extension, "wb") as writer:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                writer.write(chunk)
    return app.send_static_file(file_prefix + episode + extension)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=666)
