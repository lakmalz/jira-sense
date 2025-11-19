"""
Data Loader for ChromaDB
Loads chunked Jira data from CSV into ChromaDB with proper embeddings
Banking-compliant: Uses local sentence-transformers (no external API calls)
"""

import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
import os


class JiraDataLoader:
    """
    Handles loading Jira chunked data from CSV into ChromaDB
    Uses sentence-transformers for banking compliance (no external APIs)
    """
    
    def __init__(
        self, 
        db_path: str = "./temp/chromadb", 
        collection_name: str = "jira_content",
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize ChromaDB client and collection
        
        Args:
            db_path: Path to store ChromaDB data
            collection_name: Name of the collection to create/use
            model_name: Sentence transformer model (banking-compliant, runs locally)
                       Options:
                       - "all-MiniLM-L6-v2" (default, 80MB, fast)
                       - "all-mpnet-base-v2" (420MB, more accurate)
                       - "paraphrase-multilingual-MiniLM-L12-v2" (multilingual)
        """
        # Create directory if it doesn't exist
        os.makedirs(db_path, exist_ok=True)
        
        # Initialize sentence transformer embedding function
        self.sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=model_name
        )
        
        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection_name = collection_name
        
        # Get or create collection with sentence transformers
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.sentence_transformer_ef
            )
            print(f"✅ Loaded existing collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.sentence_transformer_ef,
                metadata={"description": "Jira issue chunks with banking-compliant embeddings"}
            )
            print(f"✅ Created new collection: {collection_name}")
        
        print(f"✅ Using model: {model_name} (runs locally, no external API calls)")
    
    def load_from_csv(self, csv_path: str, batch_size: int = 100) -> Dict[str, Any]:
        """
        Load data from CSV file into ChromaDB
        
        Args:
            csv_path: Path to the CSV file
            batch_size: Number of records to process at once
            
        Returns:
            Dictionary with loading statistics
        """
        try:
            # Read CSV file
            df = pd.read_csv(csv_path)
            print(f"Loaded {len(df)} rows from {csv_path}")
            
            # Prepare data for ChromaDB
            documents = []
            metadatas = []
            ids = []
            
            for idx, row in df.iterrows():
                # Create document text (combining title and chunk text for better search)
                doc_text = f"{row['title']}\n\n{row['chunk_text']}"
                documents.append(doc_text)
                
                # Create metadata
                metadata = {
                    "issue_key": str(row['issue_key']),
                    "chunk_id": str(row['chunk_id']),
                    "title": str(row['title']),
                    "country": str(row['Country']),
                    "content_type": self._detect_content_type(str(row['chunk_text']))
                }
                metadatas.append(metadata)
                
                # Use chunk_id as unique identifier
                ids.append(str(row['chunk_id']))
            
            # Add documents to collection in batches
            total_added = 0
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i+batch_size]
                batch_meta = metadatas[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]
                
                self.collection.add(
                    documents=batch_docs,
                    metadatas=batch_meta,
                    ids=batch_ids
                )
                total_added += len(batch_docs)
                print(f"Added {total_added}/{len(documents)} documents...")
            
            print(f"✓ Successfully loaded {total_added} documents into ChromaDB")
            
            return {
                "status": "success",
                "total_loaded": total_added,
                "collection_name": self.collection_name
            }
            
        except FileNotFoundError:
            print(f"Error: CSV file not found at {csv_path}")
            return {"status": "error", "message": "CSV file not found"}
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _detect_content_type(self, text: str) -> str:
        """
        Detect if the chunk is a description, comment, or validation rule
        
        Args:
            text: Chunk text to analyze
            
        Returns:
            Content type as string
        """
        text_lower = text.lower()
        
        if "comment from" in text_lower or "bug report" in text_lower:
            return "comment"
        elif "validation" in text_lower or "required" in text_lower:
            return "validation"
        elif "feature request" in text_lower:
            return "feature_request"
        else:
            return "description"
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the current collection
        
        Returns:
            Dictionary with collection statistics
        """
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "total_documents": count,
            "metadata": self.collection.metadata
        }
    
    def clear_collection(self):
        """
        Delete all documents from the collection
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            print(f"Deleted collection: {self.collection_name}")
            
            # Recreate empty collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Jira issue chunks with descriptions, titles, and comments"}
            )
            print(f"Created new empty collection: {self.collection_name}")
        except Exception as e:
            print(f"Error clearing collection: {str(e)}")


# Example usage
if __name__ == "__main__":
    import os
    
    # Get the parent directory (project root)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("="*100)
    print("Jira Data Loader - Banking Compliant Mode")
    print("="*100)
    
    # Initialize loader with banking-compliant settings
    loader = JiraDataLoader(
        db_path=os.path.join(project_root, "temp", "chromadb"),
        collection_name="jira_content",
        model_name="all-MiniLM-L6-v2"  # Runs locally, compliance-friendly
    )
    
    # Load data from CSV
    csv_path = os.path.join(project_root, "temp", "files", "chunked_data.csv")
    result = loader.load_from_csv(csv_path)
    
    # Get collection info
    info = loader.get_collection_info()
    print(f"\n{'='*100}")
    print("Loading Complete - Summary:")
    print(f"{'='*100}")
    print(f"  Collection Name: {info['collection_name']}")
    print(f"  Total Documents: {info['total_documents']}")
    print(f"  Status: {result['status']}")
    print(f"{'='*100}")
