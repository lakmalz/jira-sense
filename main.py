"""
Main entry point for Jira Sense - ChromaDB Search System
Run this file to access all functionality
"""

import sys
import os

# Add core directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

def show_menu():
    """Display main menu"""
    print("\n" + "="*100)
    print("JIRA SENSE - ChromaDB Search System")
    print("="*100)
    print("\nSelect an option:")
    print("1. Load CSV data into ChromaDB")
    print("2. Run search examples")
    print("3. Run case-insensitive demo")
    print("4. Run interactive pipeline")
    print("5. Exit")
    print("="*100)

def main():
    """Main entry point"""
    while True:
        show_menu()
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            print("\n📥 Loading data from CSV...")
            from core.data_loader import JiraDataLoader
            loader = JiraDataLoader(db_path="./temp/chromadb", collection_name="jira_content")
            result = loader.load_from_csv("./temp/files/chunked_data.csv")
            print(f"\nResult: {result}")
            input("\nPress Enter to continue...")
            
        elif choice == '2':
            print("\n🔍 Running search examples...")
            os.system('cd core && python search_builder.py')
            input("\nPress Enter to continue...")
            
        elif choice == '3':
            print("\n🎯 Running case-insensitive demo...")
            os.system('cd core && python demo.py')
            input("\nPress Enter to continue...")
            
        elif choice == '4':
            print("\n🚀 Starting interactive pipeline...")
            os.system('cd core && python pipeline.py')
            
        elif choice == '5':
            print("\n👋 Goodbye!")
            sys.exit(0)
            
        else:
            print("\n❌ Invalid choice. Please select 1-5.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
