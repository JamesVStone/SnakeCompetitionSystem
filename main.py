import flask
from flask import request
import json
import uuid
import logging
import hashlib
import sqlite3
from flask import g
from flask_cors import cross_origin
import os

logging.basicConfig(filename=os.environ['LOGFILE'], level=logging.INFO)
app = flask.Flask(__name__)

DATABASE = os.environ['DATABASE']


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def init_db():
    logging.info("Applying schema migrations")
    with app.app_context():
        db = get_db()
        with app.open_resource('init.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.teardown_appcontext
def close_connection(exception):
    logging.info("Database connection closed")
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


"""
TODO: handle 'game' frame data
TODO: sql for competition db
TODO: uuid generation
TODO: export data to csv?
TODO: html page sumerising current aggregation stats
"""

"""
schema:

id, ip address, timestamp, blob   
"""


@app.route('/api/game', methods=['POST'])
@cross_origin(origins=["*"], methods=["POST"])
def hook():
    addr = request.remote_addr
    data = json.loads(request.data)
    token = data['token']
    game = data['data']
    
    if len(game) < 100000000:
        con = get_db()
        cur = con.cursor()
        cur.execute('insert into games (ip_addr, token, data, timestamp) values (?, ?, ?, datetime(\'now\'))',
                    (addr, data['token'], data['data']))
        con.commit()
    return ""


@app.route('/api/uuid', methods=['GET'])
@cross_origin(origins=["*"], methods=["GET"])
def get_uuid():
    token = str(uuid.uuid4())

    response = app.response_class(
        response=json.dumps({"token": token}),
        status=200,
        mimetype='application/json'
    )

    print(f"New UUID generated for {request.remote_addr} {token}")
    return response


@app.route('/stats', methods=["GET"])
def html_stats():
    db = get_db().cursor()
    db.execute('select count(distinct token) from games')
    q1 = db.fetchall()[0][0]
    db.execute('select count(distinct ip_addr) from games')
    q2 = db.fetchall()[0][0]
    db.execute('select * from main.players')
    q3 = db.fetchall()
    db.execute('select count(*) from main.games')
    q4 = db.fetchall()[0][0]
    table = "".join([f"<tr><td>{hashlib.sha1(r[0].encode()).hexdigest()}</td><td>{r[1]}</td></tr>" for r in q3])
    return f"""<b>{q1}</b> distinct uuids<br/>
            <b>{q2}</b> distinct ips<br/>{q4} <b>Games</b><br/>
            <table>
            <tr><th>UUID</th><th>Count</th></tr>
            {table}
            </table>"""
