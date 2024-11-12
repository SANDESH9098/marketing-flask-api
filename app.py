from flask import Flask, request, jsonify
import requests
import pandas as pd
from transformers import pipeline
import os
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__)

# Set up the summarizer (using the Hugging Face transformers library)
summarizer = pipeline("summarization")

# Define access tokens and API keys (replace with your actual keys)
REDDIT_TOKEN = os.getenv("REDDIT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
DEVTO_API_KEY = os.getenv("DEVTO_API_KEY")

@app.route('/')
def index():
    return "Welcome to the Market Research API"

# # Fetch Reddit Posts
# @app.route('/fetch_reddit_posts', methods=['GET'])
# def fetch_reddit_posts():
#     subreddit = request.args.get("subreddit", "webdev")
#     sort = request.args.get("sort", "hot")
#     limit = int(request.args.get("limit", 5))
#
#     headers = {
#         "Authorization": f"Bearer {REDDIT_TOKEN}",
#         "User-Agent": "CustomGPTMarketResearch"
#     }
#     url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={limit}"
#     response = requests.get(url, headers=headers)
#
#     if response.status_code != 200:
#         return jsonify({"error": "Failed to fetch data from Reddit"}), response.status_code
#
#     posts = response.json()["data"]["children"]
#     data = [{"title": post["data"]["title"], "url": post["data"]["url"]} for post in posts]
#     return jsonify(data)


# Fetch GitHub Repositories
@app.route('/fetch_github_repos', methods=['GET'])
def fetch_github_repos():
    query = request.args.get("query", "topic:AI")
    sort = request.args.get("sort", "stars")
    order = request.args.get("order", "desc")

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "User-Agent": "CustomGPTMarketResearch"
    }
    url = "https://api.github.com/search/repositories"
    params = {"q": query, "sort": sort, "order": order}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data from GitHub"}), response.status_code

    repos = response.json()["items"]
    data = [{"name": repo["name"], "url": repo["html_url"], "stars": repo["stargazers_count"]} for repo in repos]
    return jsonify(data)


# Fetch Dev.to Articles
@app.route('/fetch_devto_articles', methods=['GET'])
def fetch_devto_articles():
    tag = request.args.get("tag", "webdev")
    top = int(request.args.get("top", 5))

    headers = {"api-key": DEVTO_API_KEY}
    url = "https://dev.to/api/articles"
    params = {"tag": tag}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data from Dev.to"}), response.status_code

    articles = response.json()
    data = [{"title": article["title"], "url": article["url"]} for article in articles[:top]]
    return jsonify(data)


# Summarize Trends
@app.route('/summarize_trends', methods=['POST'])
def summarize_trends():
    content = request.json.get("data", [])
    all_text = " ".join([entry["title"] for entry in content])

    # Generate a summary of the combined text
    summary = summarizer(all_text, max_length=50, min_length=25, do_sample=False)
    return jsonify({"summary": summary[0]["summary_text"]})


# Compile Report
@app.route('/compile_report', methods=['POST'])
def compile_report():
    data = request.json.get("data", [])
    df = pd.DataFrame(data)
    df.to_csv("market_trends_report.csv", index=False)
    return jsonify({"message": "Report generated successfully and saved as market_trends_report.csv"})


# Run Flask App
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
