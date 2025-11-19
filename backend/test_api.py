"""
Test script for FastAPI Backend
Tests all endpoints
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_build():
    """Test build endpoint"""
    print("\n" + "="*80)
    print("TEST 2: Build Database")
    print("="*80)
    
    payload = {
        "csv_path": "./temp/files/chunked_data.csv",
        "model_name": "all-MiniLM-L6-v2",
        "batch_size": 100
    }
    
    response = requests.post(
        f"{BASE_URL}/api/build",
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_search_post():
    """Test search endpoint (POST)"""
    print("\n" + "="*80)
    print("TEST 3: Search (POST) - 'Mobile no'")
    print("="*80)
    
    payload = {
        "keyword": "Mobile no",
        "n_results": 10,
        "case_sensitive": False
    }
    
    response = requests.post(
        f"{BASE_URL}/api/search",
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Total Results: {result['total_results']}")
    print(f"Message: {result['message']}")
    
    if result['results']:
        print(f"\nFirst Result:")
        print(f"  ID: {result['results'][0]['id']}")
        print(f"  Issue: {result['results'][0]['metadata']['issue_key']}")
        print(f"  Matches: {result['results'][0]['keyword_matches']}")
    
    return response.status_code == 200


def test_search_get():
    """Test search endpoint (GET)"""
    print("\n" + "="*80)
    print("TEST 4: Search (GET) - 'email address'")
    print("="*80)
    
    response = requests.get(
        f"{BASE_URL}/api/search/keyword/email%20address?n_results=5"
    )
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Total Results: {result['total_results']}")
    print(f"Message: {result['message']}")
    
    return response.status_code == 200


def test_search_with_filter():
    """Test search with country filter"""
    print("\n" + "="*80)
    print("TEST 5: Search with Filter - 'Mobile no' in Singapore")
    print("="*80)
    
    payload = {
        "keyword": "Mobile no",
        "n_results": 10,
        "country": "Singapore"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/search",
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Total Results: {result['total_results']}")
    print(f"Message: {result['message']}")
    
    return response.status_code == 200


def test_collection_info():
    """Test collection info endpoint"""
    print("\n" + "="*80)
    print("TEST 6: Collection Info")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/api/collection/info")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200


def main():
    """Run all tests"""
    print("="*80)
    print("🧪 Jira Sense API - Test Suite")
    print("="*80)
    print("\n⚠️  Make sure the server is running: python backend/start.py")
    print("⏳ Starting tests in 3 seconds...")
    sleep(3)
    
    tests = [
        ("Health Check", test_health),
        ("Build Database", test_build),
        ("Search (POST)", test_search_post),
        ("Search (GET)", test_search_get),
        ("Search with Filter", test_search_with_filter),
        ("Collection Info", test_collection_info)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
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
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("="*80)


if __name__ == "__main__":
    main()
