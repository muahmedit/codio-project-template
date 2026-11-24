from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

ALLOWED_SORT_FIELDS = {"title", "content"}
ALLOWED_DIRECTIONS = {"asc", "desc"}


def get_next_id():
    return max((post["id"] for post in POSTS), default=0) + 1


def find_post_by_id(post_id):
    return next((post for post in POSTS if post["id"] == post_id), None)


@app.route("/api/posts", methods=["GET"])
def get_posts():
    sort_field = request.args.get("sort")
    direction = request.args.get("direction", "asc")

    if sort_field is None and "direction" not in request.args:
        return jsonify(POSTS), 200

    if sort_field not in ALLOWED_SORT_FIELDS:
        return jsonify({
            "error": f"Invalid sort field '{sort_field}'. Allowed values: 'title', 'content'."
        }), 400

    if direction not in ALLOWED_DIRECTIONS:
        return jsonify({
            "error": f"Invalid sort direction '{direction}'. Allowed values: 'asc', 'desc'."
        }), 400

    reverse = direction == "desc"
    sorted_posts = sorted(
        POSTS,
        key=lambda post: str(post.get(sort_field, "")).lower(),
        reverse=reverse,
    )
    return jsonify(sorted_posts), 200


@app.route("/api/posts", methods=["POST"])
def add_post():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be valid JSON",
            "missing_fields": ["title", "content"],
        }), 400

    missing_fields = [
        field for field in ("title", "content")
        if not data.get(field) or not str(data.get(field)).strip()
    ]

    if missing_fields:
        return jsonify({
            "error": f"Missing required field(s): {', '.join(missing_fields)}",
            "missing_fields": missing_fields,
        }), 400

    new_post = {
        "id": get_next_id(),
        "title": str(data["title"]).strip(),
        "content": str(data["content"]).strip(),
    }
    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    post = find_post_by_id(post_id)
    if post is None:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    POSTS.remove(post)
    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200


@app.route("/api/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    post = find_post_by_id(post_id)
    if post is None:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON."}), 400

    if "title" in data and data["title"] is not None:
        post["title"] = str(data["title"])
    if "content" in data and data["content"] is not None:
        post["content"] = str(data["content"])

    return jsonify(post), 200


@app.route("/api/posts/search", methods=["GET"])
def search_posts():
    title_query = (request.args.get("title") or "").strip().lower()
    content_query = (request.args.get("content") or "").strip().lower()

    if not title_query and not content_query:
        return jsonify([]), 200

    matching_posts = []
    for post in POSTS:
        post_title = str(post.get("title", "")).lower()
        post_content = str(post.get("content", "")).lower()

        title_match = bool(title_query) and title_query in post_title
        content_match = bool(content_query) and content_query in post_content

        if title_match or content_match:
            matching_posts.append(post)

    return jsonify(matching_posts), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)