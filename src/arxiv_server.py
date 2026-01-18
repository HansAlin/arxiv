from flask import Flask, send_from_directory, make_response
from arxiv_presentaion import ArxivHtmlRenderer
from pathlib import Path




BASE_DIR = Path(__file__).resolve().parent.parent  # project root (one level above src/)
HTML_PATH = BASE_DIR / "html" / "arxiv_digest.html"
JSON_PATH = BASE_DIR / "states" / "arxiv_results.json"

# Explicitly set static folder to project root
app = Flask(__name__, static_folder=str(BASE_DIR / "static"))



@app.route("/")
def index():
    # Render the latest HTML
    renderer = ArxivHtmlRenderer(
        input_json=JSON_PATH,
        output_html=HTML_PATH
    )
    renderer.render()

    # Send HTML file with headers to prevent caching
    response = make_response(send_from_directory(HTML_PATH.parent, HTML_PATH.name))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
