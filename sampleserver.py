from flask import Flask, redirect, render_template, request, url_for, session, make_response, Response, jsonify
import os, psycopg2, requests, random


app = Flask(__name__)

@app.route('/index/')
def index():
    return render_template('index.html')

app.secret_key = os.urandom(24)

@app.route('/authorize')
def authorize():
    return "authorized"

@app.route('/helloworld')
def helloworld():
    return "Hello World!"

@app.route('/sushi')
def sushi():
    return redirect("https://www.bing.com/videos/search?q=extream+kshmr+youtube&view=detail&mid=9ACA9B516D32E71E58669ACA9B516D32E71E5866&FORM=VIRE")

@app.route('/home')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return "Hello Boss!  <a href='/logout'>Logout</a>"

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'user':
        session['logged_in'] = True
    else:
        return "Wrong Password!"
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
                            password='training', host='192.168.2.10',
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

@app.route('/flip')
def flip():
    return random.choice(["Head","Tail"])

@app.route('/roll/<n>')
def roll(n):
    sum = 0
    for i in range(1,int(n)+1):
        sum = sum + random.choice([1,2,3,4,5,6])
    return str(sum)

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
    app.run(debug=False, host='0.0.0.0', port=666)
