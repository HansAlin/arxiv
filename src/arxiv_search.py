#!/home/pi/Projects/arxiv/env/bin/python
import arxiv
from datetime import datetime, timedelta, timezone
import json
import pickle
import os

class ArxivSearch():
	def __init__(self, state_path='states/', search_state_file="state.json"):

		# Construct the default API client.
		self.client = arxiv.Client()

		# State folder
		self.state_path = state_path
		os.makedirs(self.state_path, exist_ok=True)

		# Get end date of search
		self.end_date = datetime.now(timezone.utc)

		# Search result path
		self.search_result_file_json = None
		self.search_result_file_pkl = None

		# Set result path
		self.search_result_file_json = os.path.join(self.state_path, 'arxiv_results.json')
		self.search_result_file_pkl = os.path.join(self.state_path, "arxiv_results.pkl")

		# Get previously results
		try:
			self.results = self.load_results()
		except Exception:
			self.results = None


		# Get state of last search
		self.state_file_path = os.path.join(self.state_path,search_state_file)
		self.state = {}

		# Determine start date of search
		if os.path.exists(self.state_file_path):
			self._load_state()
			self.start_date = datetime.fromisoformat(self.state['start_date'])

		else:
			# No state exists: set end_date to 10 days before today
			self.start_date = self.end_date - timedelta(days=10)

		# Search attributes
		self.search_obj = None
		self.query = self.set_query()

	def set_query(self) -> str:

		categories = (
			"(cat:hep-ex OR "
			"cat:hep-ph OR "
			"cat:nucl-ex)"
		)

		detector_keywords = (
			'"calorimeter" OR '
			'"hadronic calorimeter" OR '
			'"HCAL" OR '
			'"test beam" OR '
			'"detector calibration" OR '
			'"cosmic ray" OR '
			'"cosmic muon"'
		)

		pileup_keywords = (
			'"pileup" OR '
			'"pile-up" OR '
			'"HL-LHC" OR '
			'"high luminosity LHC" OR '
			'"event reconstruction" OR '
			'"jet reconstruction" OR '
			'"particle flow" OR '
			'"underlying event"'
		)

		experiment_keywords = (
			'"fixed target" OR '
			'"missing momentum" OR '
			'"missing energy" OR '
			'"beam dump"'
		)

		physics_keywords = (
			'"light dark matter" OR '
			'"dark photon" OR '
			'"hidden sector" OR '
			'"dark bremsstrahlung" OR '
			'"sub-GeV" OR '
			'"electron beam" OR '
			'"machine learning" OR '
			'"deep learning"'
		)

		experiment_names = (
			'"LDMX" OR '
			'"NA64" OR '
			'"PADME" OR '
			'"DarkLight" OR '
			'"NA62" OR '
			'"Belle II" OR '
			'"ATLAS" OR '
			'"CMS"'
		)

		exclude_cosmo = (
			'NOT ("cosmology" OR '
			'"CMB" OR '
			'"large scale structure" OR '
			'"relic density" OR '
			'"galaxy formation")'
		)

		# Key change: require detector/pileup/experiment context
		core = (
			"("
			f"{detector_keywords} OR "
			f"{pileup_keywords} OR "
			f"{experiment_keywords} OR "
			f"{experiment_names}"
			")"
		)

		optional = (
			"("
			f"{physics_keywords}"
			")"
		)

		self.query = f"{categories} AND {core} AND {optional} {exclude_cosmo}"

		return self.query



	def run_search(self, max_results=100, query=None):
		""" Make a search on arXive based on self.query

		Args:
			max_results (int, optional): The maximum of results from arXive. Defaults to 100.
			query (str, optional): A query defined as in self.set_query(). Defaults to None.

		Returns:
			json: The results from arxive
		"""
		print(f"Start search date {self.start_date}", end=" ,")
		print(f"End search date: {self.end_date}", end=" ")
		if query is None:
			query = self.query

		
		self.search = arxiv.Search(
		query = query,
		max_results = max_results,
		sort_by = arxiv.SortCriterion.SubmittedDate
		)


		filtered_results = []
		for result in self.client.results(self.search):
			if self.start_date <= result.published <= self.end_date:
				filtered_results.append({
					"title": result.title,
					"authors": [str(a) for a in result.authors],
					"abstract": result.summary,
					"published": result.published.isoformat(),
					"updated": result.updated.isoformat(),
					"pdf": result.pdf_url
				})
		
		if filtered_results is None or len(filtered_results) == 0:
			print("No new items found!", end=" ")
			filtered_results = self.results
			return filtered_results
		else:
			print(f"{len(filtered_results)} items found!", end=" ")
			filtered_results = self.remove_resubmissions(results=filtered_results)
			
			self.start_date = self.end_date
			self._save_state()

			self.results = filtered_results

			return filtered_results

	def remove_resubmissions(self, results):
		""" Removes all the articles that is a resubmission from a previous submission

		Args:
			results (json): Gives the filterd json back
		"""
		length_before_filtering = len(results)
		filtered_results = []
		for article in results:

			if article["published"] == article["updated"]:
				filtered_results.append(article)
		results_after_filtering = len(filtered_results)

		print(f"Number of articles before filtering: {length_before_filtering} and after: {results_after_filtering}")

		self._save_results(results=filtered_results)


	def _save_results(self, results):
		"""Saves the results from the arXive search to a json file and pkl file

		Args:
			filtered_results (_type_): _description_
		"""

		with open(self.search_result_file_json, "w", encoding="utf-8") as f:
			json.dump(results, f, ensure_ascii=False, indent=2)


		with open(self.search_result_file_pkl, "wb") as f:
			pickle.dump(results, f)

	def load_results(self,):
		""" Load the results from a created json file from a 
		    previous arXiv search

		Returns:
			json: content in search dict json
		"""

		with open(self.search_result_file_json, 'r', encoding="utf-8") as f:
			self.results = json.load(f)

		return self.results

	def _save_state(self):
		""" Save the current search state, for next search to know where to start search from

		"""

		self.state["start_date"] = self.start_date.isoformat()


		with open(self.state_file_path, "w", encoding="utf-8") as f:
			json.dump(self.state, f, ensure_ascii=False, indent=4)

	def _load_state(self):
		""" Loads the stored information about previous search on arXive
		"""
		with open(self.state_file_path, "r", encoding="utf-8") as f:
			self.state = json.load(f)

		self.start_date = datetime.fromisoformat(self.state["start_date"])





if __name__ == '__main__':
	arx = ArxivSearch()
	results = arx.run_search()
	
	