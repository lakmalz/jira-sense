"""
Quick Start Guide for Jira Sense Search System
"""

import sys
import os

# Add core directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

# STEP 1: Install dependencies
# pip install chromadb pandas

# STEP 2: Load data into ChromaDB (one-time setup)
from core.data_loader import JiraDataLoader

loader = JiraDataLoader(db_path="./temp/chromadb", collection_name="jira_content")
result = loader.load_from_csv("./temp/files/chunked_data.csv")
print(f"Loaded {result['total_loaded']} documents")

# STEP 3: Search the database
from core.search_builder import JiraSearchBuilder

searcher = JiraSearchBuilder(db_path="./temp/chromadb", collection_name="jira_content")

# Search for "Mobile no" (case-insensitive)
# This will match: mobile no, Mobile Number, MOBILE NO, mobile_no, etc.
results = searcher.search_by_keyword("Mobile no", n_results=50)

# Display results
searcher.format_results(results)

# Get total count
print(f"Total matches: {len(results)}")

# EXAMPLE SEARCHES:

# 1. Search for mobile number variations
results = searcher.search_by_keyword("Mobile no")
# Finds: "mobile no", "Mobile Number", "MOBILE NO", "mobile_no"

# 2. Search for email address variations  
results = searcher.search_by_keyword("email address")
# Finds: "email address", "Email Address", "e-mail address", "EMAIL ADDRESS"

# 3. Search for username variations
results = searcher.search_by_keyword("username")
# Finds: "username", "Username", "USER NAME", "user_name"

# 4. Search with country filter
results = searcher.search_by_keyword("Mobile no", where={"country": "Singapore"})
# Only finds results from Singapore

# 5. Search for "new email address"
results = searcher.search_by_keyword("new email address")
# Finds all documents mentioning "new email address"

# 6. Search for "old email address"
results = searcher.search_by_keyword("old email address")
# Finds all documents mentioning "old email address"

# 7. Get all data in collection
all_data = searcher.get_all_data()
print(f"Total documents: {len(all_data['ids'])}")

# RESULT STRUCTURE:
# Each result is a dictionary with:
# {
#     'id': 'BCBD-492537-2',
#     'document': 'Full text content...',
#     'metadata': {
#         'issue_key': 'BCBD-492537',
#         'chunk_id': 'BCBD-492537-2',
#         'title': '[SG] Fund transfer...',
#         'country': 'Singapore',
#         'content_type': 'validation'
#     },
#     'keyword_matches': ['Mobile no', 'mobile number'],
#     'match_count': 2,
#     'similarity': 0.6234,
#     'distance': 0.3766
# }

# KEY FEATURES:
# ✓ Case-insensitive search
# ✓ Matches keyword variations (no ↔ number)
# ✓ Handles different separators (space, hyphen, underscore)
# ✓ Ranked by relevance (match count + similarity)
# ✓ Rich metadata (issue key, country, content type)
# ✓ Semantic search + keyword filtering

# QUICK COMMANDS:
# python data_loader.py      # Load CSV into ChromaDB
# python search_builder.py   # Run example searches
# python demo.py             # Run case-insensitive demo
# python pipeline.py         # Run complete pipeline with interactive mode
