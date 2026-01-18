import os
from slack_sdk import WebClient
import json


class SlackMessenger():

	def __init__(self, content_json_path='states/arxiv_results.json', bot_name="Arxiv messenger", max_articles=10) -> None:
		
		# Set the maximum numbe rof articles to send_message
		self.max_articles = max_articles

		# Path to message content
		self.content_json_path = content_json_path

		# Bot name
		self.bot_name = bot_name

		# Instanciate the Slack client
		self.slack_token = os.environ.get("SLACK_TOKEN")

		if self.slack_token is None:
			assert "No Slack token provided"
		self.client = WebClient(token=self.slack_token)

		self.full_message = None
		
	def create_slack_message_from_arxiv(self,):

		# Load your JSON file
		with open(self.content_json_path, "r", encoding="utf-8") as f:
			data = json.load(f)

		# Transform each entry into a Slack-friendly message
		slack_messages = []

		

		for i, paper in enumerate(data):
			if i + 1 > self.max_articles:
				break
			title = paper.get("title", "No Title")
			authors = ", ".join(paper.get("authors", []))
			abstract = paper.get("abstract", "No abstract available")
			published = paper.get("published", "Unknown date")
			pdf_url = paper.get("pdf", "")

			# Convert to a Slack-friendly text block
			message = (
				f"*{title}*\n"
				f"_Authors:_ {authors}\n"
				f"_Published:_ {published}\n"
				f"_PDF:_ <{pdf_url}|Click here to open>\n"
				f"_Abstract:_ {abstract}\n"
			)
			slack_messages.append(message)

		# Join all messages if you want a single post
		self.full_message = "\n\n---\n\n".join(slack_messages)

		return self.full_message
	
	def send_message(self, slack_message):
		self.client.chat_postMessage(
				channel="bot-updates",
				text=slack_message,
				username=self.bot_name
			)



if __name__ == "__main__":

	slack_messenger = SlackMessenger( content_json_path='states/arxiv_results.json', max_articles=5)
	message = slack_messenger.create_slack_message_from_arxiv()
	slack_messenger.send_message(slack_message=message)

