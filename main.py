import os
import json
from dotenv import load_dotenv
from src.agent import ClaimsAgent
from src.pdf_processor import PDFProcessor

load_dotenv()

def main():
    agent = ClaimsAgent()
    pdf_processor = PDFProcessor()
    
    data_dir = "data/raw"
    results = {}

    if not os.path.exists(data_dir):
        print(f"Error: {data_dir} directory not found.")
        return

    for filename in os.listdir(data_dir):
        file_path = os.path.join(data_dir, filename)
        print(f"Processing {filename}...")
        
        try:
            if filename.endswith(".pdf"):
                text_content = pdf_processor.extract_text_from_pdf(file_path)
                if text_content and len(text_content.strip()) > 100:
                    content_for_llm = text_content
                else:
                    print(f"Text extraction from {filename} was poor. Gemini-only mode requires text input.")
                    results[filename] = {
                        "error": "PDF text extraction failed; Gemini-only mode does not support image fallback."
                    }
                    continue
            else:
                with open(file_path, 'r') as f:
                    content_for_llm = f.read()
            
            result = agent.process_claim(content_for_llm)
            results[filename] = result
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            results[filename] = {"error": str(e)}

    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nProcessing complete. Results saved to results.json")
    for filename, res in results.items():
        route = res.get('recommendedRoute', 'Error')
        print(f"- {filename}: {route}")

if __name__ == "__main__":
    main()
