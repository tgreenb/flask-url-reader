from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

app = Flask(__name__)
ALLOWED_DOMAINS = ["openai.com", "help.openai.com"]

@app.route('/read-url', methods=['GET'])
def read_url():
    url_to_fetch = request.args.get('url')
    if not url_to_fetch:
        return jsonify({"error": "URL parameter is required."}), 400
    try:
        parsed_url = urlparse(url_to_fetch)
        if not parsed_url.scheme.startswith("http"):
            return jsonify({"error": "Only http and https URLs are allowed."}), 400
        domain = parsed_url.netloc.lower()
        domain = domain[4:] if domain.startswith("www.") else domain
        if domain not in ALLOWED_DOMAINS:
            return jsonify({"error": f"Access to the domain {domain} is not allowed."}), 403
    except Exception as e:
        return jsonify({"error": f"Invalid URL format: {str(e)}"}), 400

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url_to_fetch, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        article_body = soup.find('article') or soup.find('main') or soup.body
        page_text = article_body.get_text(separator='\n', strip=True) if article_body else "Content not found."
        return jsonify({"results": page_text})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch the URL: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
