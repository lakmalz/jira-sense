"""
Demo Script: Shows case-insensitive search working with keyword variations
"""

import sys
import os

# Add the parent directory to the path so we can import from core
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from search_builder import JiraSearchBuilder


def demo_search(searcher, keyword, description):
    """Helper function to perform and display search"""
    print("\n" + "="*100)
    print(f"🔎 {description}")
    print(f"   Keyword: '{keyword}'")
    print("="*100)
    
    results = searcher.search_by_keyword(keyword, n_results=50)
    
    if results:
        print(f"\n✓ Found {len(results)} matching documents\n")
        
        # Show first 3 results with highlights
        for idx, result in enumerate(results[:3], 1):
            print(f"\n📄 Result {idx}:")
            print(f"   Issue: {result['metadata']['issue_key']}")
            print(f"   Country: {result['metadata']['country']}")
            print(f"   Matches found: {', '.join(set(result['keyword_matches']))}")
            print(f"   Match count: {result['match_count']}")
            print(f"   Preview: {result['document'][:150]}...")
            print("-"*100)
    else:
        print(f"\n✗ No matches found for '{keyword}'")


def main():
    print("\n" + "="*100)
    print("🎯 JIRA SENSE - CASE-INSENSITIVE SEARCH DEMO")
    print("="*100)
    print("\nDemonstrating how the search finds variations of keywords:")
    print("- 'Mobile no' matches: mobile no, Mobile Number, MOBILE NO, mobile_no, etc.")
    print("- 'email address' matches: Email Address, e-mail address, EMAIL ADDRESS, etc.")
    print("\n🏦 Banking Compliant: All processing runs locally, no external API calls")
    
    # Get the parent directory (project root)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Initialize searcher with banking-compliant settings
    searcher = JiraSearchBuilder(
        db_path=os.path.join(project_root, "temp", "chromadb"),
        collection_name="jira_content",
        model_name="all-MiniLM-L6-v2"  # Runs locally, no external API
    )
    
    # Demo 1: Mobile no (lowercase)
    demo_search(
        searcher,
        "mobile no",
        "Demo 1: Searching for 'mobile no' (lowercase)"
    )
    
    # Demo 2: MOBILE NUMBER (uppercase)
    demo_search(
        searcher,
        "MOBILE NUMBER",
        "Demo 2: Searching for 'MOBILE NUMBER' (uppercase)"
    )
    
    # Demo 3: Email Address (title case)
    demo_search(
        searcher,
        "Email Address",
        "Demo 3: Searching for 'Email Address' (title case)"
    )
    
    # Demo 4: e-mail address (with hyphen)
    demo_search(
        searcher,
        "e-mail address",
        "Demo 4: Searching for 'e-mail address' (with hyphen)"
    )
    
    # Demo 5: username
    demo_search(
        searcher,
        "username",
        "Demo 5: Searching for 'username'"
    )
    
    # Demo 6: User Name (with space)
    demo_search(
        searcher,
        "User Name",
        "Demo 6: Searching for 'User Name' (with space)"
    )
    
    # Demo 7: New email address
    demo_search(
        searcher,
        "new email address",
        "Demo 7: Searching for 'new email address'"
    )
    
    # Demo 8: old email address
    demo_search(
        searcher,
        "old email address",
        "Demo 8: Searching for 'old email address'"
    )
    
    print("\n" + "="*100)
    print("✅ DEMO COMPLETED")
    print("="*100)
    print("\nKey Takeaways:")
    print("1. ✓ Case-insensitive: 'mobile no' = 'Mobile No' = 'MOBILE NO'")
    print("2. ✓ Variation matching: 'no' = 'number', 'e-mail' = 'email'")
    print("3. ✓ Flexible separators: spaces, hyphens, underscores all match")
    print("4. ✓ Ranked by relevance: More matches = higher ranking")
    print("\nTo run interactive search: python pipeline.py")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
