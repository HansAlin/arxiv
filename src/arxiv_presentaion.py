import json
from datetime import datetime, timedelta
from pathlib import Path


class ArxivHtmlRenderer:
	"""
	Render arXiv search results into a clean, readable HTML page
	with MathJax support for LaTeX in abstracts.
	"""

	def __init__(self, input_json: str, output_html: str = "html/arxiv_digest.html"):
		self.input_json = Path(input_json)
		self.output_html = Path(output_html)



	def input_updated_within(self, hours=24) -> bool:
		if not self.input_json.exists():
			return False

		mtime = datetime.fromtimestamp(self.input_json.stat().st_mtime)
		return datetime.now() - mtime < timedelta(hours=hours)


	def load_papers(self):
		with open(self.input_json, "r", encoding="utf-8") as f:
			papers = json.load(f)

		# Sort newest first (by published date)
		papers.sort(
			key=lambda p: p.get("published", ""),
			reverse=True
		)
		return papers

	def render(self, max_age_hours=24):
		if self.output_html.exists() and not self.input_updated_within(max_age_hours):
			print("Input unchanged — keeping existing HTML.")
			return

		papers = self.load_papers()
		html = self._build_html(papers)

		self.output_html.parent.mkdir(parents=True, exist_ok=True)

		with open(self.output_html, "w", encoding="utf-8") as f:
			f.write(html)

		print(f"HTML digest updated: {self.output_html.resolve()}")



	def _build_html(self, papers):
		generated_time = datetime.now().strftime("%Y-%m-%d %H:%M")
		parts = []

		# ---------- HTML HEADER ----------
		parts.append(f"""<!DOCTYPE html>
	<html lang="en">
	<head>
	<meta charset="utf-8">
	<title>arXiv Digest</title>

	<!-- MathJax for LaTeX rendering -->
	<script>
	window.MathJax = {{
	tex: {{
		inlineMath: [['$', '$'], ['\\\\(', '\\\\)']]
	}}
	}};
	</script>
	<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

	<!-- Link to external CSS -->
	<link rel="stylesheet" href="/static/style.css">
	</head>
	<body>
	<h1>arXiv Digest</h1>
	<div class="meta">Generated: {generated_time} </div>
	""")

		# ---------- PAPERS ----------
		for p in papers:
			title = p.get("title", "Untitled")
			authors_list = p.get("authors", [])
			authors = ", ".join(authors_list[:5])
			if len(authors_list) > 5:
				authors += " et al."
			abstract = p.get("abstract", "")
			published = p.get("published", "")
			pdf = p.get("pdf", "#")
			parts.append(f"""
	<div class="paper">
	<div class="title"><a href="{pdf}" target="_blank">{title}</a></div>
	<div class="authors">{authors}</div>
	<div class="pubdate">Published: {published}</div>
	<details>
		<summary>Abstract</summary>
		<div class="abstract">{abstract}</div>
	</details>
	</div>
	""")

		# ---------- FOOTER ----------
		parts.append("""
	</body>
	</html>
	""")
		return "\n".join(parts)


if __name__ == "__main__":
	renderer = ArxivHtmlRenderer(
		input_json="states/arxiv_results.json",
		output_html="html/arxiv_digest.html"
	)

	renderer.render()