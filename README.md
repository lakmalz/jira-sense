# Jira Sense - ChromaDB Search Pipeline

A complete pipeline for loading and searching Jira chunked data using ChromaDB with case-insensitive keyword matching.

**🏦 Banking-Compliant**: Uses local `sentence-transformers` - no external API calls, all processing on-premises.

## Project Structure

```
jira_sense/
├── main.py                 # Main entry point with menu
├── core/                   # Core classes
│   ├── data_loader.py     # JiraDataLoader class
│   ├── search_builder.py  # JiraSearchBuilder class
│   ├── demo.py            # Demo script
│   └── pipeline.py        # Complete pipeline
├── temp/                   # Temporary data storage
│   ├── files/             # CSV data files
│   │   └── chunked_data.csv
│   └── chromadb/          # ChromaDB database storage
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Features

- ✅ Load CSV data into ChromaDB with automatic embedding
- ✅ Case-insensitive keyword search ("Mobile no" matches "MOBILE NO", "mobile number", etc.)
- ✅ Semantic search with keyword filtering
- ✅ Separate classes for data loading and searching
- ✅ Support for metadata filtering (country, content type, etc.)
- ✅ Interactive search mode
- 🏦 **Banking-Compliant**: Uses local sentence-transformers (all-MiniLM-L6-v2)
  - No external API calls
  - All processing on-premises
  - Data never leaves your infrastructure
  - GDPR/SOC2 friendly

## Embedding Model

**Model**: `all-MiniLM-L6-v2` (sentence-transformers)
- **Size**: 80MB
- **Dimensions**: 384
- **Speed**: Fast
- **Privacy**: Runs 100% locally
- **Banking-Compliant**: ✅ No external API calls

### Alternative Models (Banking-Compliant)

You can change the model in the code:

```python
# More accurate (420MB)
loader = JiraDataLoader(model_name="all-mpnet-base-v2")
searcher = JiraSearchBuilder(model_name="all-mpnet-base-v2")

# Multilingual support (420MB, 50+ languages)
loader = JiraDataLoader(model_name="paraphrase-multilingual-MiniLM-L12-v2")
searcher = JiraSearchBuilder(model_name="paraphrase-multilingual-MiniLM-L12-v2")
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Option 1: Use Main Menu (Recommended)

```bash
python main.py
```

This provides an interactive menu with all options:
1. Load CSV data into ChromaDB
2. Run search examples
3. Run case-insensitive demo
4. Run interactive pipeline
5. Exit

### Option 2: Run Complete Pipeline

```bash
cd core
python pipeline.py
```

This will:
1. Load data from `temp/files/chunked_data.csv` into ChromaDB
2. Perform sample searches
3. Enter interactive search mode

### Option 3: Load Data Only

```bash
cd core
python data_loader.py
```

### Option 4: Search Only

```bash
cd core
python search_builder.py
```

### Option 5: Run Demo

```bash
cd core
python demo.py
```

## Code Structure

### 1. `core/data_loader.py` - JiraDataLoader Class

Handles loading CSV data into ChromaDB:

```python
from core.data_loader import JiraDataLoader

# Initialize loader
loader = JiraDataLoader(db_path="./temp/chromadb", collection_name="jira_content")

# Load data from CSV
result = loader.load_from_csv("./temp/files/chunked_data.csv")

# Get collection info
info = loader.get_collection_info()
```

### 2. `core/search_builder.py` - JiraSearchBuilder Class

Handles searching with case-insensitive matching:

```python
from core.search_builder import JiraSearchBuilder

# Initialize searcher
searcher = JiraSearchBuilder(db_path="./temp/chromadb", collection_name="jira_content")

# Search for keyword (case-insensitive)
results = searcher.search_by_keyword("Mobile no", n_results=50)

# Display results
searcher.format_results(results)

# Get all data
all_data = searcher.get_all_data()
```

### 3. `core/pipeline.py` - Complete Pipeline

Orchestrates the entire workflow with interactive search.

### 4. `core/demo.py` - Demo Script

Demonstrates case-insensitive search with various examples.

## Search Examples

### Example 1: Search for "Mobile no"

```python
results = searcher.search_by_keyword("Mobile no")
```

**Matches:**
- "Mobile no"
- "mobile number"
- "MOBILE NO"
- "Mobile Number"
- "mobile_no"
- "mobile-number"

### Example 2: Search for "email address"

```python
results = searcher.search_by_keyword("email address")
```

**Matches:**
- "email address"
- "Email Address"
- "E-mail address"
- "EMAIL ADDRESS"
- "email_address"

### Example 3: Search with Filter

```python
# Search only in Singapore issues
results = searcher.search_by_keyword(
    keyword="Mobile no",
    where={"country": "Singapore"}
)
```

## Key Features

### Case-Insensitive Matching
The search automatically handles all case variations:
- `searcher.search_by_keyword("Mobile no")` matches "MOBILE NO", "mobile number", etc.

### Keyword Variations
Automatically matches common variations:
- "no" ↔ "number"
- Handles spaces, hyphens, underscores

### Rich Results
Each result includes:
- Document ID and content
- Metadata (issue key, title, country, content type)
- Keyword matches found
- Match count
- Similarity score

## Data Format

CSV file should be located at `temp/files/chunked_data.csv` with these columns:
- `issue_key`: Jira issue identifier
- `chunk_id`: Unique chunk identifier
- `title`: Issue title
- `chunk_text`: Text content of the chunk
- `Country`: Country/region code

## Storage Locations

- **CSV Data**: `temp/files/chunked_data.csv`
- **ChromaDB**: `temp/chromadb/` (automatically created)
- **Core Classes**: `core/` directory

## Notes

- ChromaDB data is stored in the `./temp/chromadb` directory
- CSV files are stored in the `./temp/files` directory
- Core classes are in the `./core` directory
- The system uses semantic search + keyword filtering for best results
- All searches are case-insensitive by default
- Results are ranked by match count and similarity score
- **Banking-Compliant**: Uses `sentence-transformers` locally - no data sent to external APIs
- **Privacy**: All processing happens on your infrastructure
- **Model**: all-MiniLM-L6-v2 (80MB, 384 dimensions, runs locally)


echo "# jira-sense" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M master
git remote add origin https://github.com/lakmalz/jira-sense.git
git push -u origin master