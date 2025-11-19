#!/usr/bin/env python3
"""
Test Script - Verify All Components
Run this to ensure everything is working correctly
"""

import os
import sys

def test_imports():
    """Test if all imports work"""
    print("="*80)
    print("TEST 1: Checking Imports")
    print("="*80)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
        from data_loader import JiraDataLoader
        from search_builder import JiraSearchBuilder
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_paths():
    """Test if all required paths exist"""
    print("\n" + "="*80)
    print("TEST 2: Checking Paths")
    print("="*80)
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    paths = {
        "CSV File": os.path.join(project_root, "temp", "files", "chunked_data.csv"),
        "ChromaDB Dir": os.path.join(project_root, "temp", "chromadb"),
        "Core Package": os.path.join(project_root, "core", "__init__.py"),
        "Data Loader": os.path.join(project_root, "core", "data_loader.py"),
        "Search Builder": os.path.join(project_root, "core", "search_builder.py"),
    }
    
    all_exist = True
    for name, path in paths.items():
        exists = os.path.exists(path)
        status = "✅" if exists else "❌"
        print(f"{status} {name}: {path}")
        if not exists:
            all_exist = False
    
    return all_exist

def test_data_load():
    """Test if data can be loaded"""
    print("\n" + "="*80)
    print("TEST 3: Testing Data Load")
    print("="*80)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
        from data_loader import JiraDataLoader
        
        project_root = os.path.dirname(os.path.abspath(__file__))
        loader = JiraDataLoader(
            db_path=os.path.join(project_root, "temp", "chromadb"),
            collection_name="jira_content"
        )
        
        info = loader.get_collection_info()
        print(f"✅ Collection: {info['collection_name']}")
        print(f"✅ Documents: {info['total_documents']}")
        return info['total_documents'] > 0
    except Exception as e:
        print(f"❌ Data load failed: {e}")
        return False

def test_search():
    """Test if search works"""
    print("\n" + "="*80)
    print("TEST 4: Testing Search")
    print("="*80)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
        from search_builder import JiraSearchBuilder
        
        project_root = os.path.dirname(os.path.abspath(__file__))
        searcher = JiraSearchBuilder(
            db_path=os.path.join(project_root, "temp", "chromadb"),
            collection_name="jira_content"
        )
        
        # Test search
        results = searcher.search_by_keyword("Mobile no", n_results=10)
        print(f"✅ Search completed")
        print(f"✅ Found {len(results)} results for 'Mobile no'")
        return len(results) > 0
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("JIRA SENSE - SYSTEM TEST")
    print("="*80 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("Paths", test_paths),
        ("Data Load", test_data_load),
        ("Search", test_search),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 ALL TESTS PASSED! System is ready to use.")
        print("Run 'python main.py' to start the interactive menu.")
    else:
        print("⚠️  SOME TESTS FAILED. Please check the errors above.")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
