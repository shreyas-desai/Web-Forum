from flask import Flask,request,jsonify
import secrets
from datetime import datetime,timezone

from secrets import randbelow
app = Flask(__name__)

posts = []

@app.route('/post', methods=['POST'])
def create_post():
    try:
        data = request.get_json()

        if not isinstance(data, dict) or 'msg' not in data or not isinstance(data['msg'], str):
            return jsonify({"error": "Bad request. Missing or invalid 'msg' field."}), 400

        post_id = len(posts) + 1

        key = secrets.token_urlsafe(32)

        timestamp = datetime.now(timezone.utc).isoformat()

        post = {
            "id": post_id,
            "key": key,
            "timestamp": timestamp,
            "msg": data['msg']
        }

        posts.append(post)
        return jsonify(post), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500

@app.route('/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    try:
        post = next((p for p in posts if p['id'] == post_id), None)

        if not post:
            return jsonify({"error": "Post not found"}), 404

        return jsonify({"id": post['id'], "timestamp": post['timestamp'], "msg": post['msg']}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500

@app.route('/post/<int:post_id>/delete/<string:key>', methods=['DELETE'])
def delete_post(post_id, key):
    try:
        post = next((p for p in posts if p['id'] == post_id), None)

        if not post:
            return jsonify({"error": "Post not found"}), 404

        if post['key'] != key:
            return jsonify({"error": "Forbidden. Incorrect key"}), 403

        posts.remove(post)

        return jsonify({"id": post['id'], "key": post['key'], "timestamp": post['timestamp']}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)