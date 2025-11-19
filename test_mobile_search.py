"""
Test script to check if 'Mobile no' data is available in ChromaDB
"""

import sys
import os

# Add the core directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from search_builder import JiraSearchBuilder

def test_mobile_search():
    """
    Test if 'Mobile no' data exists in the database
    """
    print("="*100)
    print("Testing 'Mobile no' Search")
    print("="*100)
    
    try:
        # Initialize search builder
        searcher = JiraSearchBuilder(
            db_path="./temp/chromadb",
            collection_name="jira_content",
            model_name="all-MiniLM-L6-v2"
        )
        
        # Method 1: Keyword search (case-insensitive with pattern matching)
        print("\n📋 METHOD 1: Keyword Search for 'Mobile no'")
        print("-"*100)
        keyword_results = searcher.search_by_keyword("Mobile no", n_results=50)
        
        if keyword_results:
            print(f"✅ Found {len(keyword_results)} results using keyword search")
            print("\nTop 3 Results:")
            searcher.format_results(keyword_results[:3], show_full_doc=False)
        else:
            print("❌ No results found using keyword search")
        
        # Method 2: Semantic search (finds conceptually similar content)
        print("\n\n📋 METHOD 2: Semantic Search for 'Mobile no'")
        print("-"*100)
        semantic_results = searcher.semantic_search("Mobile no", n_results=10)
        
        if semantic_results:
            print(f"✅ Found {len(semantic_results)} results using semantic search")
            print("\nTop 3 Results:")
            for idx, result in enumerate(semantic_results[:3]):
                print(f"\n📄 Result #{idx + 1}")
                print(f"ID: {result['id']}")
                print(f"Similarity: {result['similarity']:.4f}")
                if result['metadata']:
                    print(f"Issue Key: {result['metadata'].get('issue_key', 'N/A')}")
                    print(f"Title: {result['metadata'].get('title', 'N/A')}")
                print(f"Document Preview: {result['document'][:200]}...")
                print("-"*100)
        else:
            print("❌ No results found using semantic search")
        
        # Method 3: Check all data for "mobile" related content
        print("\n\n📋 METHOD 3: Checking all documents for 'mobile' mentions")
        print("-"*100)
        all_data = searcher.get_all_data()
        
        if all_data and all_data.get('documents'):
            mobile_docs = []
            for idx, doc in enumerate(all_data['documents']):
                if 'mobile' in doc.lower():
                    mobile_docs.append({
                        'id': all_data['ids'][idx],
                        'document': doc,
                        'metadata': all_data['metadatas'][idx] if all_data['metadatas'] else None
                    })
            
            if mobile_docs:
                print(f"✅ Found {len(mobile_docs)} documents containing 'mobile'")
                print("\nSample documents:")
                for idx, doc in enumerate(mobile_docs[:3]):
                    print(f"\n📄 Document #{idx + 1}")
                    print(f"ID: {doc['id']}")
                    if doc['metadata']:
                        print(f"Issue Key: {doc['metadata'].get('issue_key', 'N/A')}")
                        print(f"Title: {doc['metadata'].get('title', 'N/A')}")
                    print(f"Content: {doc['document'][:300]}...")
                    print("-"*100)
            else:
                print("❌ No documents found containing 'mobile'")
        
        # Summary
        print("\n\n" + "="*100)
        print("📊 SUMMARY")
        print("="*100)
        print(f"Keyword Search Results: {len(keyword_results)}")
        print(f"Semantic Search Results: {len(semantic_results)}")
        print(f"Total Documents in DB: {len(all_data.get('documents', []))}")
        
        if len(keyword_results) > 0:
            print("\n✅ 'Mobile no' data IS AVAILABLE and can be retrieved!")
            print("\nRecommended usage:")
            print("  searcher.search_by_keyword('Mobile no', n_results=50)")
            print("  searcher.semantic_search('Mobile no', n_results=10)")
        else:
            print("\n⚠️  'Mobile no' data NOT FOUND in the database")
            print("Possible reasons:")
            print("  1. Data not loaded yet - run: python core/data_loader.py")
            print("  2. CSV file doesn't contain 'Mobile no' keyword")
            print("  3. Check CSV file content: temp/files/chunked_data.csv")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Make sure ChromaDB is built: python core/data_loader.py")
        print("  2. Check if CSV file exists: temp/files/chunked_data.csv")
        print("  3. Verify ChromaDB path: temp/chromadb")


if __name__ == "__main__":
    test_mobile_search()
