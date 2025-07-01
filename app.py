from flask import Flask, request, jsonify, abort
import pandas as pd
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# Load Excel data once on startup
df = pd.read_excel("data.xlsx")
data = df.to_dict(orient="records")

app = Flask(__name__)

# API key for auth
API_KEY = "72D3GUc3niGzxKZ8HZMYVEfPdodrIj"  # Replace with a secure value or use env vars

# Rate limiting: 100 requests/hour per IP
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"]
)

@app.before_request
def check_auth():
    # Apply auth only to GET /items
    if request.endpoint == "get_items":
        token = request.headers.get("Authorization")
        if token != f"Bearer {API_KEY}":
            abort(401, description="Unauthorized")

@app.route("/items")
def get_items():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        return jsonify({"error": "Invalid page or per_page value"}), 400

    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = data[start:end]

    return jsonify({
        "page": page,
        "per_page": per_page,
        "total": len(data),
        "data": paginated_data
    })

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"error": str(e)}), 401

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify({"error": "Rate limit exceeded"}), 429

if __name__ == "__main__":
    app.run()
