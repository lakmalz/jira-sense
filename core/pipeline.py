"""
Complete Pipeline: Load Jira data into ChromaDB and perform searches
Demonstrates the full workflow from CSV to searchable database
"""

import sys
import os

# Add the parent directory to the path so we can import from core
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import JiraDataLoader
from search_builder import JiraSearchBuilder


def main():
    """
    Main pipeline execution
    """
    print("="*100)
    print("JIRA DATA PIPELINE - Load and Search")
    print("="*100)
    
    # Get the parent directory (project root)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Configuration
    DB_PATH = os.path.join(project_root, "temp", "chromadb")
    COLLECTION_NAME = "jira_content"
    CSV_FILE = os.path.join(project_root, "temp", "files", "chunked_data.csv")
    
    # Step 1: Load data into ChromaDB
    print("\n📥 STEP 1: Loading data from CSV into ChromaDB (Banking-Compliant Mode)...")
    print("-"*100)
    
    loader = JiraDataLoader(
        db_path=DB_PATH, 
        collection_name=COLLECTION_NAME,
        model_name="all-MiniLM-L6-v2"  # Runs locally, no external API
    )
    
    # Check if collection already has data
    info = loader.get_collection_info()
    if info['total_documents'] > 0:
        print(f"⚠️  Collection already contains {info['total_documents']} documents.")
        response = input("Do you want to reload the data? (yes/no): ").lower()
        if response == 'yes':
            print("Clearing existing collection...")
            loader.clear_collection()
            result = loader.load_from_csv(CSV_FILE)
        else:
            print("Using existing data.")
            result = {"status": "skipped", "total_loaded": info['total_documents']}
    else:
        result = loader.load_from_csv(CSV_FILE)
    
    if result['status'] in ['success', 'skipped']:
        print(f"✓ Data ready: {result.get('total_loaded', 0)} documents in collection")
    else:
        print(f"✗ Error loading data: {result.get('message', 'Unknown error')}")
        sys.exit(1)
    
    # Step 2: Initialize search
    print("\n\n🔍 STEP 2: Initializing Search Engine (Banking-Compliant Mode)...")
    print("-"*100)
    
    try:
        searcher = JiraSearchBuilder(
            db_path=DB_PATH, 
            collection_name=COLLECTION_NAME,
            model_name="all-MiniLM-L6-v2"  # Runs locally, no external API
        )
        print("✓ Search engine ready")
    except Exception as e:
        print(f"✗ Error initializing search: {str(e)}")
        sys.exit(1)
    
    # Step 3: Perform searches
    print("\n\n📊 STEP 3: Performing Sample Searches...")
    print("-"*100)
    
    # Search 1: Mobile no
    print("\n🔎 Search Query: 'Mobile no'")
    print("Searching for all variations: mobile no, Mobile Number, MOBILE NO, etc.")
    print("-"*100)
    results = searcher.search_by_keyword("Mobile no", n_results=50)
    searcher.format_results(results[:3])  # Show top 3
    print(f"\n✓ Total matches found: {len(results)}")
    
    # Search 2: Email address
    print("\n\n🔎 Search Query: 'email address'")
    print("Searching for all variations: email address, e-mail address, Email Address, etc.")
    print("-"*100)
    results = searcher.search_by_keyword("email address", n_results=50)
    searcher.format_results(results[:3])  # Show top 3
    print(f"\n✓ Total matches found: {len(results)}")
    
    # Search 3: Username
    print("\n\n🔎 Search Query: 'username'")
    print("Searching for all variations: username, user name, Username, etc.")
    print("-"*100)
    results = searcher.search_by_keyword("username", n_results=50)
    searcher.format_results(results[:3])  # Show top 3
    print(f"\n✓ Total matches found: {len(results)}")
    
    # Interactive search
    print("\n\n" + "="*100)
    print("💡 INTERACTIVE SEARCH MODE")
    print("="*100)
    
    while True:
        print("\nEnter a search keyword (or 'quit' to exit):")
        keyword = input("🔎 Search: ").strip()
        
        if keyword.lower() in ['quit', 'exit', 'q']:
            print("Exiting pipeline. Goodbye!")
            break
        
        if not keyword:
            print("Please enter a valid keyword.")
            continue
        
        print(f"\nSearching for: '{keyword}'...")
        results = searcher.search_by_keyword(keyword, n_results=50)
        
        if results:
            searcher.format_results(results[:5])  # Show top 5
            print(f"\n✓ Total matches found: {len(results)}")
            
            # Ask if user wants to see more
            if len(results) > 5:
                show_more = input("\nShow all results? (yes/no): ").lower()
                if show_more == 'yes':
                    searcher.format_results(results[5:], show_full_doc=False)
        else:
            print(f"No results found for '{keyword}'")
        
        print("\n" + "-"*100)


if __name__ == "__main__":
    main()
