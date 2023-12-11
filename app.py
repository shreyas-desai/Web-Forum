from flask import Flask,request,jsonify
import secrets
from datetime import datetime,timezone
import sqlite3
from threading import Lock

app = Flask(__name__)
lock = Lock()

conn = sqlite3.connect('posts.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        key TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        msg TEXT NOT NULL
    )
''')
conn.commit()
conn.close()
# posts = []

@app.route('/post', methods=['POST'])
def create_post():
    try:
        conn = sqlite3.connect('posts.db', check_same_thread=False)
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

@app.route('/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    try:
        conn = sqlite3.connect('posts.db', check_same_thread=False)
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
        conn = sqlite3.connect('posts.db', check_same_thread=False)
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