"""
ChromaDB Search Builder for Jira Content
Retrieves relevant chunked data from Jira descriptions, titles, and comments
Case-insensitive search with keyword variations
Banking-compliant: Uses local sentence-transformers (no external API calls)
"""

import chromadb
from chromadb.utils import embedding_functions
import re
from typing import List, Dict, Any, Optional


class JiraSearchBuilder:
    """
    A class to handle searching and retrieving data from ChromaDB
    containing Jira-related content (descriptions, titles, comments)
    Supports case-insensitive search with keyword variations
    
    Banking Compliance:
    - Uses local sentence-transformers (no external API calls)
    - All processing happens on-premises
    - No data leaves your infrastructure
    """
    
    def __init__(
        self, 
        db_path: str = "./temp/chromadb", 
        collection_name: str = "jira_content",
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the ChromaDB client and collection
        
        Args:
            db_path: Path to the ChromaDB database directory
            collection_name: Name of the collection containing Jira data
            model_name: Sentence transformer model to use (default: all-MiniLM-L6-v2)
                       Banking-suitable options:
                       - "all-MiniLM-L6-v2" (default, 80MB, fast)
                       - "all-mpnet-base-v2" (420MB, more accurate)
                       - "paraphrase-multilingual-MiniLM-L12-v2" (multilingual)
        """
        # Initialize ChromaDB with sentence transformers
        self.sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=model_name
        )
        
        self.client = chromadb.PersistentClient(path=db_path)
        try:
            # Get collection with the same embedding function
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.sentence_transformer_ef
            )
            print(f"✅ Connected to collection: {collection_name}")
            print(f"✅ Using model: {model_name} (runs locally, banking-compliant)")
        except Exception as e:
            raise Exception(f"Collection '{collection_name}' not found. Please load data first using data_loader.py")
    
    def search_by_keyword(
        self, 
        keyword: str, 
        n_results: int = 50,
        where: Optional[Dict[str, Any]] = None,
        case_sensitive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents using a keyword query (case-insensitive by default)
        Finds all variations: "Mobile no", "mobile number", "MOBILE NO", etc.
        
        Args:
            keyword: The search keyword (e.g., "Mobile no")
            n_results: Maximum number of results to retrieve for filtering (default: 50)
            where: Optional metadata filter
            case_sensitive: If True, performs case-sensitive search (default: False)
            
        Returns:
            List of dictionaries containing matched documents with metadata
        """
        # First, do semantic search to get relevant documents
        semantic_results = self.collection.query(
            query_texts=[keyword],
            n_results=n_results,
            where=where
        )
        
        # Then filter results to ensure they actually contain the keyword (case-insensitive)
        filtered_results = self._filter_by_keyword(
            semantic_results, 
            keyword, 
            case_sensitive=case_sensitive
        )
        
        return filtered_results
    
    def _filter_by_keyword(
        self, 
        results: Dict[str, Any], 
        keyword: str, 
        case_sensitive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Filter search results to only include documents that contain the keyword
        Supports case-insensitive matching
        
        Args:
            results: Raw results from ChromaDB query
            keyword: Keyword to search for
            case_sensitive: Whether to use case-sensitive matching
            
        Returns:
            List of filtered results with the keyword highlighted
        """
        filtered = []
        
        if not results['ids'] or len(results['ids'][0]) == 0:
            return filtered
        
        # Create regex pattern for flexible matching (inlined)
        # This will match variations like "mobile no", "Mobile Number", "MOBILE NO", etc.
        # Build pattern and flags here instead of calling a separate helper method
        keyword_escaped = re.escape(keyword)
        flexible_pattern = keyword_escaped.replace(r'\ ', r'[\s\-_]*')
        pattern = r'\b' + flexible_pattern + r'\b'
        variations = [pattern]

        # If keyword contains "no" also match "number" and vice versa
        if re.search(r'\bno\b', keyword, re.IGNORECASE):
            alt_pattern = re.sub(r'\\bno\\b', r'(no|number)', flexible_pattern, flags=re.IGNORECASE)
            variations.append(r'\b' + alt_pattern + r'\b')
        if re.search(r'\bnumber\b', keyword, re.IGNORECASE):
            alt_pattern = re.sub(r'\\bnumber\\b', r'(no|number)', flexible_pattern, flags=re.IGNORECASE)
            variations.append(r'\b' + alt_pattern + r'\b')

        keyword_pattern = '|'.join(variations)
        flags = 0 if case_sensitive else re.IGNORECASE
        
        for idx in range(len(results['ids'][0])):
            document = results['documents'][0][idx]

            # Check if keyword pattern exists in document
            if re.search(keyword_pattern, document, flags):
                # Find all matches in the document
                matches = re.findall(keyword_pattern, document, flags)

                filtered.append({
                    'id': results['ids'][0][idx],
                    'document': document,
                    'metadata': results['metadatas'][0][idx] if results['metadatas'] else None,
                    'distance': results['distances'][0][idx] if results['distances'] else None,
                    'similarity': 1 - results['distances'][0][idx] if results['distances'] else None,
                    'keyword_matches': matches,
                    'match_count': len(matches)
                })
        
        # Sort by match count (documents with more occurrences first), then by similarity
        filtered.sort(key=lambda x: (-x['match_count'], x['distance'] if x['distance'] else float('inf')))
        
        return filtered
    
    # NOTE: _create_keyword_pattern removed — pattern construction is inlined into _filter_by_keyword
    
    def get_all_data(self) -> Dict[str, Any]:
        """
        Retrieve ALL documents from the collection
        
        Returns:
            Dictionary containing all ids, documents, metadatas
        """
        all_data = self.collection.get()
        return all_data
    
    def search_with_filters(
        self,
        keyword: str,
        content_type: Optional[str] = None,  # e.g., "description", "title", "comment"
        n_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search with additional metadata filters
        
        Args:
            keyword: The search keyword
            content_type: Filter by content type (description/title/comment)
            n_results: Number of results to return
            
        Returns:
            Dictionary containing filtered search results
        """
        where_filter = None
        if content_type:
            where_filter = {"content_type": content_type}
        
        return self.search_by_keyword(
            keyword=keyword,
            n_results=n_results,
            where=where_filter
        )
    
    def search_all_matching(
        self,
        keyword: str,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Get all documents matching the keyword above a similarity threshold
        
        Args:
            keyword: The search keyword
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of matching documents with metadata
        """
        # Get a large number of results first
        results = self.search_by_keyword(keyword, n_results=1000)
        
        matched_docs = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for idx, distance in enumerate(results['distances'][0]):
                # ChromaDB returns distances (lower is better)
                # Convert to similarity score
                similarity = 1 - distance
                
                if similarity >= similarity_threshold:
                    matched_docs.append({
                        'id': results['ids'][0][idx],
                        'document': results['documents'][0][idx],
                        'metadata': results['metadatas'][0][idx] if results['metadatas'] else None,
                        'similarity': similarity,
                        'distance': distance
                    })
        
        return matched_docs
    
    def format_results(self, results: List[Dict[str, Any]], show_full_doc: bool = False) -> None:
        """
        Pretty print search results
        
        Args:
            results: List of result dictionaries
            show_full_doc: Whether to show full document or truncated version
        """
        if not results:
            print("No results found.")
            return
        
        print(f"\nFound {len(results)} results:\n")
        print("=" * 100)
        
        for idx, result in enumerate(results):
            print(f"\n📄 Result #{idx + 1}")
            print(f"ID: {result['id']}")
            
            # Show metadata
            if result['metadata']:
                print(f"Issue Key: {result['metadata'].get('issue_key', 'N/A')}")
                print(f"Title: {result['metadata'].get('title', 'N/A')}")
                print(f"Country: {result['metadata'].get('country', 'N/A')}")
                print(f"Content Type: {result['metadata'].get('content_type', 'N/A')}")
            
            # Show keyword matches
            if result.get('keyword_matches'):
                unique_matches = list(set(result['keyword_matches']))
                print(f"Keyword Matches ({result['match_count']}): {', '.join(unique_matches)}")
            
            # Show similarity score
            if result['similarity'] is not None:
                print(f"Similarity Score: {result['similarity']:.4f}")
            
            # Show document content
            doc_text = result['document']
            if show_full_doc:
                print(f"\nDocument:\n{doc_text}")
            else:
                # Show first 300 characters
                preview = doc_text[:300] + "..." if len(doc_text) > 300 else doc_text
                print(f"\nDocument Preview:\n{preview}")
            
            print("-" * 100)
