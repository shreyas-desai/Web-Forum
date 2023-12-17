import json
from flask import Flask, request, jsonify
import secrets
from datetime import datetime, timezone, timedelta
import sqlite3
from threading import Lock

app = Flask(__name__)
lock = Lock()


def getDateFromString(dt_str):
    dt, _, us = dt_str.partition(".")
    dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")

    # Extract microseconds and handle the '00:00' part
    us_part = us.split()[0]
    us = int(us_part.rstrip("Z"), 10) if us_part else 0

    return dt + timedelta(microseconds=us)


conn = sqlite3.connect('web_forum.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS posts')
cursor.execute('DROP TABLE IF EXISTS users')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        uname TEXT NOT NULL UNIQUE,
        fname TEXT NOT NULL,
        lname TEXT NOT NULL,
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
        parent_post INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (parent_post) REFERENCES posts (id)
    )
''')
conn.commit()
conn.close()
# posts = []

# POSTS


@app.route('/post', methods=['POST'])
def create_post():
    try:
        conn = sqlite3.connect('web_forum.db', check_same_thread=False)
        cursor = conn.cursor()
        data = request.get_json()

        if not isinstance(data, dict) or 'msg' not in data or not isinstance(data['msg'], str):
            conn.close()
            return jsonify({"error": "Bad request. Missing or invalid 'msg' field."}), 400

        if 'parent_post' not in data:
            parent_post_id = None
        else:
            parent_post_id = data['parent_post']
            cursor.execute("SELECT 1 FROM posts WHERE id = ?",
                           (parent_post_id,))
            exists = cursor.fetchone()
            if exists is None:
                conn.close()
                return jsonify({"error": f"Post with id {parent_post_id} Not Found"}), 404
        key = secrets.token_urlsafe(32)

        timestamp = datetime.now(timezone.utc).isoformat()

        with lock:
            cursor.execute('INSERT INTO posts (key, timestamp, msg, parent_post) VALUES (?, ?, ?, ?)',
                           (key, timestamp, data['msg'], parent_post_id))
            post_id = cursor.lastrowid

        post = {
            "id": post_id,
            "key": key,
            "timestamp": timestamp,
            "msg": data['msg']
        }

        if parent_post_id is not None:
            post["parent_post"] = parent_post_id
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

        if 'parent_post' not in data:
            parent_post_id = None
        else:
            parent_post_id = data['parent_post']
            cursor.execute("SELECT 1 FROM posts WHERE id = ?",
                           (parent_post_id,))
            exists = cursor.fetchone()
            if exists is None:
                conn.close()
                return jsonify({"error": f"Post with id {parent_post_id} Not Found"}), 404
        key = secrets.token_urlsafe(32)

        timestamp = datetime.now(timezone.utc).isoformat()

        with lock:
            cursor.execute('INSERT INTO posts (key, timestamp, msg, user_id,parent_post) VALUES (?, ?, ?, ?, ?)',
                           (key, timestamp, data['msg'], user_id, parent_post_id))
            post_id = cursor.lastrowid

        post = {
            "id": post_id,
            "key": key,
            "timestamp": timestamp,
            "msg": data['msg'],
            "user_id": user_id
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
        conn = sqlite3.connect('web_forum.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
        post_data = cursor.fetchone()
        if not post_data:
            conn.close()
            return jsonify({"error": "Post not found"}), 404
        cursor.execute(
            'SELECT id FROM posts WHERE parent_post = ?', (post_id,))
        child_posts = []
        for i in cursor.fetchall():
            child_posts.append(i[0])
        print(child_posts)

        post = {
            "id": post_data[0],
            "timestamp": post_data[2],
            "msg": post_data[3]

        }

        if post_data[4] is not None:
            post["user"] = post_data[4]
        if post_data[5] is not None:
            post["parent_post"] = post_data[5]
        if len(child_posts) != 0:
            post["child_posts"] = child_posts

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


@app.route('/post', methods=['GET'])
def get_post_with_user():
    try:
        user = request.args.get('user')

        try:
            user = int(user)
        except ValueError:
            pass
        print(type(user))
        conn = sqlite3.connect('web_forum.db', check_same_thread=False)
        cursor = conn.cursor()
        if isinstance(user, int):
            print("user_id given")
            user_id = user
            cursor.execute('SELECT * FROM posts WHERE user_id = ?', (user_id,))
            post_data = cursor.fetchall()
            if not post_data:
                conn.close()
                return jsonify({"error": f"Posts not found for user id '{user_id}'"}), 404
            cursor.execute('SELECT uname FROM users WHERE id = ?', (user_id,))
            user_name = cursor.fetchone()[0]

        if isinstance(user, str):
            print("user_name given")
            cursor.execute('SELECT id FROM users WHERE uname = ?', (user,))
            user_id = cursor.fetchone()
            if not user_id:
                conn.close()
                return jsonify({"error": f"Posts not found for user name'{user}'"}), 404
            user_id = user_id[0]
            cursor.execute('SELECT * FROM posts WHERE user_id = ?', (user_id,))
            post_data = cursor.fetchall()

        if not post_data:
            conn.close()
            return jsonify({"error": f"Posts not found for user id '{user}'"}), 404

        posts = []
        for post in post_data:
            current_post = {
                "id": post[0],
                "timestamp": post[2],
                "msg": post[3],
                "user_id": user_id,
                "uname": user_name
            }
            if post[5] is not None:
                current_post["parent_post"] = post[5]
            cursor.execute(
                'SELECT id FROM posts WHERE parent_post = ?', (post[0],))
            child_posts = []
            for i in cursor.fetchall():
                child_posts.append(i[0])
            print(child_posts)

            if len(child_posts) != 0:
                current_post["child_posts"] = child_posts
            posts.append(current_post)
        for post in posts:
            print(post)
        row = cursor.execute(
            'SELECT * from posts where user_id = ?', (user_id,))
        for i in row.fetchall():
            print(i)
        conn.commit()
        conn.close()
        return jsonify(posts), 200

    except Exception as e:
        print(e)
        conn.close()
        return jsonify({"error": "Internal server error"}), 500


@app.route('/postsByDate', methods=['GET'])
def get_post_by_date():
    try:
        print(request.args)
        startDate = request.args.get('startDate')
        print(startDate)

        endDate = request.args.get('endDate')
        print(endDate)

        start_datetime = ''
        end_datetime = ''
        start_date_str = ''
        end_date_str = ''

        if (startDate is None and endDate is None):
            return jsonify({"error": "Bad request. Missing or invalid 'startDate' and 'endDate' fields."}), 400

        try:
            if startDate is not None:
                startDate = getDateFromString(startDate)
                start_date_str = startDate.strftime('%Y-%m-%d %H:%M:%S')

            if endDate is not None:
                endDate = getDateFromString(endDate)
                end_date_str = endDate.strftime('%Y-%m-%d %H:%M:%S')

            if (endDate < startDate):
                return jsonify({"error": "Bad request. 'endDate' should be greater than 'startDate'"}), 400

            # end_datetime = datetime.strptime(endDate, '%Y-%m-%dT%H:%M:%S.%f')

            # Format startDate and endDate as strings in 'YYYY-MM-DD HH:mm:ss' format

        except ValueError as e:
            print(e)
        print(startDate, endDate)
        conn = sqlite3.connect('web_forum.db', check_same_thread=False)
        cursor = conn.cursor()

        if startDate is not None and endDate is not None:
            cursor.execute(
                'SELECT * FROM posts WHERE timestamp BETWEEN ? AND ?', (start_date_str, end_date_str,))
        elif startDate is not None:
            cursor.execute(
                'SELECT * FROM posts WHERE timestamp >= ?', (start_date_str,))
        elif endDate is not None:
            cursor.execute(
                'SELECT * FROM posts WHERE timestamp <= ?', (end_date_str,))
        else:
            conn.close()
            return jsonify({"error": "Bad request. Missing 'startDate' or 'endDate' field."}), 400

        post_data = cursor.fetchall()
        if not post_data:
            conn.close()
            return jsonify({"error": f"Posts not found for given date range"}), 404
        posts = []
        for post in post_data:
            current_post = {
                "id": post[0],
                "timestamp": post[2],
                "msg": post[3],
            }
            if post[4] is not None:
                current_post["user_id"] = post[4]
            if post[5] is not None:
                current_post["parent_post"] = post[5]
            cursor.execute(
                'SELECT id FROM posts WHERE parent_post = ?', (post[0],))
            child_posts = []
            for i in cursor.fetchall():
                child_posts.append(i[0])
            print(child_posts)

            if len(child_posts) != 0:
                current_post["child_posts"] = child_posts
            posts.append(current_post)

        conn.commit()
        conn.close()
        return jsonify(posts), 200

    except Exception as e:
        print(e)
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
        user_key = None
        if post_data[4] != None:
            cursor.execute("SELECT key FROM users where id = ?",
                           (post_data[4],))
            user_key = cursor.fetchone()[0]
            print(user_key)

        if post_data[1] != key and key != user_key:
            conn.close()
            return jsonify({"error": "Forbidden. Incorrect key"}), 403
        deleted_with = ["Deleted with user key." if user_key !=
                        None and key == user_key else "Deleted with post key."]
        with lock:
            cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        post = {
            "id": post_data[0],
            "key": post_data[1],
            "timestamp": post_data[2],
            "msg": post_data[3],
            "deleted_with": deleted_with[0]
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

# USERS


@app.route('/user', methods=['POST'])
def create_user():
    try:
        conn = sqlite3.connect('web_forum.db', check_same_thread=False)
        cursor = conn.cursor()
        data = request.get_json()
        if not isinstance(data, dict) or 'uname' not in data or not isinstance(data['uname'], str):
            conn.close()
            return jsonify({"error": "Bad request. Missing or invalid 'uname' field."}), 400
        if 'fname' not in data or 'lname' not in data or not isinstance(data['fname'], str) or not isinstance(data['lname'], str):
            conn.close()
            return jsonify({"error": "Bad request. Missing or invalid 'fname' and 'lname' fields."}), 400
        key = secrets.token_urlsafe(32)

        time_created = datetime.now(timezone.utc).isoformat()

        try:
            with lock:
                cursor.execute('INSERT INTO users (key, time_created, uname, fname, lname) VALUES (?, ?, ?, ?, ?)',
                               (key, time_created, data['uname'], data['fname'], data['lname']))
                user_id = cursor.lastrowid
        except sqlite3.IntegrityError as e:
            print("error", e)
            conn.close()
            return jsonify({"error": f"Bad request. Username already taken"}), 403
        except Exception as e:
            print("error", e)
            conn.close()
            return jsonify({"error": "Internal server error"}), 500

        user = {
            "id": user_id,
            "uname": data['uname'],
            "fname": data['fname'],
            "lname": data['lname'],
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
        if not conn.closed:
            conn.close()
        return jsonify({"error": "Internal server error"}), 500


@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_with_id(user_id):
    try:
        conn = sqlite3.connect('web_forum.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users where id = ?", (user_id,))
        user_data = cursor.fetchone()
        if not user_data:
            conn.close()
            return jsonify({"error": f"User with id {user_id} not found"}), 404
        user = {
            "id": user_data[0],
            "time_created": user_data[4],
            "fname": user_data[2],
            "lname": user_data[3],
            "uname": user_data[1]
        }
        row = cursor.execute('SELECT * from users')
        for i in row.fetchall():
            print(i)
        conn.commit()
        conn.close()
        return jsonify(user), 200

    except Exception as e:
        print(e)
        conn.close()
        return jsonify({"error": "Internal server error"}), 500


@app.route('/user/<string:uname>', methods=['GET'])
def get_user_with_uname(uname):
    try:
        conn = sqlite3.connect('web_forum.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users where uname = ?", (uname,))
        user_data = cursor.fetchone()
        if not user_data:
            conn.close()
            return jsonify({"error": f"User with username {uname} not found"}), 404
        user = {
            "id": user_data[0],
            "time_created": user_data[4],
            "fname": user_data[2],
            "lname": user_data[3],
            "uname": user_data[1]
        }
        row = cursor.execute('SELECT * from users')
        for i in row.fetchall():
            print(i)
        conn.commit()
        conn.close()
        return jsonify(user), 200

    except Exception as e:
        print(e)
        conn.close()
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=True)
