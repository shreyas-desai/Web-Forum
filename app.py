from flask import Flask,request,jsonify
import secrets
from datetime import datetime,timezone
import sqlite3
from threading import Lock

app = Flask(__name__)
lock = Lock()

conn = sqlite3.connect('web_forum.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS posts')
cursor.execute('DROP TABLE IF EXISTS users')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        uname TEXT NOT NULL,
        time_created TEXT NOT NULL,
        key TEXT NOT NULL
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        key TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        msg TEXT NOT NULL,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')
conn.commit()
conn.close()
# posts = []

@app.route('/post', methods=['POST'])
def create_post():
    try:
        conn = sqlite3.connect('web_forum.db', check_same_thread=False)
        cursor = conn.cursor()
        data = request.get_json()

        if not isinstance(data, dict) or 'msg' not in data or not isinstance(data['msg'], str):
            conn.close()
            return jsonify({"error": "Bad request. Missing or invalid 'msg' field."}), 400

        key = secrets.token_urlsafe(32)

        timestamp = datetime.now(timezone.utc).isoformat()

        with lock:
            cursor.execute('INSERT INTO posts (key, timestamp, msg) VALUES (?, ?, ?)',
                           (key, timestamp, data['msg']))
            post_id = cursor.lastrowid


        post = {
            "id": post_id,
            "key": key,
            "timestamp": timestamp,
            "msg": data['msg']
        }
        row = cursor.execute('SELECT * from posts')
        for i in row.fetchall():
            print(i)
        conn.commit()
        conn.close()
        return jsonify(post), 200

    except Exception as e:
        print(e)
        if not conn.closed:
            conn.close()
        return jsonify({"error": "Internal server error"}), 500

@app.route('/post/<int:user_id>', methods=['POST'])
def create_post_with_user(user_id):
    try:
        conn = sqlite3.connect('web_forum.db', check_same_thread=False)
        cursor = conn.cursor()
        data = request.get_json()

        cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
        post_w_user = cursor.fetchone()
        if not post_w_user:
            conn.close()
            return jsonify({"error": f"Bad request. No user with id {user_id} found!"}), 404

        if not isinstance(data, dict) or 'msg' not in data or not isinstance(data['msg'], str):
            conn.close()
            return jsonify({"error": "Bad request. Missing or invalid 'msg' field."}), 400

        key = secrets.token_urlsafe(32)

        timestamp = datetime.now(timezone.utc).isoformat()

        with lock:
            cursor.execute('INSERT INTO posts (key, timestamp, msg, user_id) VALUES (?, ?, ?, ?)',
                            (key, timestamp, data['msg'], user_id))
            post_id = cursor.lastrowid

        post = {
            "id": post_id,
            "key": key,
            "timestamp": timestamp,
            "msg": data['msg'],
            "user_id":user_id
        }
        row = cursor.execute('SELECT * from posts')
        for i in row.fetchall():
            print(i)
        conn.commit()
        conn.close()
        return jsonify(post), 200
    except Exception as e:
        print(e)
        if not conn.closed:
            conn.close()
        return jsonify({"error": "Internal server error"}), 500

@app.route('/user',methods=['POST'])
def create_user():
    try:
        conn = sqlite3.connect('web_forum.db', check_same_thread=False)
        cursor = conn.cursor()
        data = request.get_json()
        if not isinstance(data, dict) or 'uname' not in data or not isinstance(data['uname'], str):
            conn.close()
            return jsonify({"error": "Bad request. Missing or invalid 'uname' field."}), 400
        cursor.execute("SELECT * FROM users WHERE uname = ?",(data['uname'],))
        post_w_user = cursor.fetchone()
        if post_w_user:
            conn.close()
            return jsonify({"error": f"Bad request. Username already taken"}), 403
        key = secrets.token_urlsafe(32)

        time_created = datetime.now(timezone.utc).isoformat()

        with lock:
            cursor.execute('INSERT INTO users (key, time_created, uname) VALUES (?, ?, ?)',
                            (key, time_created, data['uname']))
            user_id = cursor.lastrowid
        user = {
            "id": user_id,
            "uname": data['uname'],
            "time_created": time_created
        }
        row = cursor.execute('SELECT * from users')
        for i in row.fetchall():
            print(i)
        conn.commit()
        conn.close()
        return jsonify(user), 200

    except Exception as e:
        print(e)

@app.route('/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    try:
        conn = sqlite3.connect('web_forum.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
        post_data = cursor.fetchone()
        if not post_data:
            conn.close()
            return jsonify({"error": "Post not found"}), 404
        post={
            "id":post_data[0],
            "timestamp":post_data[2],
            "msg":post_data[3],
        }
        row = cursor.execute('SELECT * from posts')
        for i in row.fetchall():
            print(i)
        conn.commit()
        conn.close()
        return jsonify(post), 200

    except Exception as e:
        print(e)
        if not conn.closed:
            conn.close()
        return jsonify({"error": "Internal server error"}), 500

@app.route('/post/<int:post_id>/delete/<string:key>', methods=['DELETE'])
def delete_post(post_id, key):
    try:
        conn = sqlite3.connect('web_forum.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
        post_data = cursor.fetchone()
        if not post_data:
            conn.close()
            return jsonify({"error": "Post not found"}), 404

        if post_data[1] != key:
            conn.close()
            return jsonify({"error": "Forbidden. Incorrect key"}), 403
        with lock:
            cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        post={
            "id":post_data[0],
            "key":post_data[1],
            "timestamp":post_data[2]
            # "msg":post_data[3],
        }
        row = cursor.execute('SELECT * from posts')
        for i in row.fetchall():
            print(i)
        conn.commit()
        conn.close()
        return jsonify(post), 200

    except Exception as e:
        print(e)
        if not conn.closed:
            conn.close()
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)