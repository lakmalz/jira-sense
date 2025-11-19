import os
from pathlib import Path

from data_loader import JiraDataLoader
from search_builder import JiraSearchBuilder
PROJECT_ROOT = Path(__file__).parent.parent

class JiraReader:
    def __init__(self):
        self.output_dir = "temp"
        self.input_file = "res/jira_stories.csv"
        self.db_path = os.path.join(PROJECT_ROOT, "temp", "chromadb")
        self.collection_name = "jira_content"
        self.loader = JiraDataLoader(
            db_path=self.db_path,
            collection_name=self.collection_name,
            model_name="all-MiniLM-L6-v2"
        )
        self.searcher = JiraSearchBuilder(
            db_path=self.db_path,
            collection_name=self.collection_name,
            model_name="all-MiniLM-L6-v2"
        )
        os.makedirs(self.output_dir, exist_ok=True)

    def indexing(self):
        return self.loader.load_from_csv("temp/jira_stories_chunked.csv")

    def search_key(self, word: str):
            return self.searcher.search_by_keyword(word, n_results=30)    
    
if __name__ == "__main__":
    print("🚀 Starting Mobile Search Tests")
    reader = JiraReader()
    # reader.indexing()
    result  = reader.search_key("Mobile no")
    print(f"Found {len(result)} results for 'Mobile no'")
    print(f"Found :{result}")
