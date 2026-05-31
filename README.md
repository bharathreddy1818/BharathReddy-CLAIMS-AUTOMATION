# Autonomous Insurance Claims Processing Agent

This project implements a lightweight autonomous agent for processing First Notice of Loss (FNOL) documents in the insurance industry. The agent extracts key fields, validates the data, classifies the claim, and routes it to the appropriate workflow.

## Features

- **Multimodal Extraction**: Uses LLMs to extract structured data from both text-based (TXT) and image-based (PDF) FNOL documents.
- **Data Validation**: Identifies missing or inconsistent mandatory fields.
- **Intelligent Routing**: Classifies claims based on predefined rules:
  - **Fast-track**: For claims with estimated damage < $25,000.
  - **Manual Review**: If any mandatory field is missing.
  - **Investigation Flag**: If the description contains suspicious keywords (e.g., "fraud", "staged").
  - **Specialist Queue**: For specific claim types like "injury".
- **Reasoning**: Provides a clear explanation for the routing decision.

## Architecture

The project consists of the following components:

1.  **`src/agent.py`**: The core logic for the agent. It handles communication with the OpenAI API for field extraction, performs validation, and applies routing rules.
2.  **`src/pdf_processor.py`**: A utility class for handling PDF documents. It attempts text extraction first and falls back to converting PDF pages to base64 images for multimodal LLM processing if the text extraction is insufficient.
3.  **`main.py`**: The entry point script that iterates through the sample documents in the `data/raw` directory, processes them using the agent, and saves the results to `results.json`.

## Prerequisites

- Python 3.8+
- OpenAI API Key (set as an environment variable `OPENAI_API_KEY`) or Google Cloud credentials for Gemini
- System dependencies for PDF processing: `poppler-utils` (for `pdftotext` and `pdf2image`)

## Installation

1.  Clone the repository:
    ```bash
    git clone <repository_url>
    cd insurance_agent
    ```

2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3.  Ensure system dependencies are installed (Ubuntu/Debian example):
    ```bash
    sudo apt-get update
    sudo apt-get install -y poppler-utils
    ```

4.  Configure Gemini with your API key, either in environment variables or in `.env`:
    ```powershell
    setx GEMINI_API_KEY "your_gemini_api_key_here"
    setx GEMINI_MODEL "gemini-1.5-mini"
    ```

    Or use a local `.env` file in the project root:
    ```text
    GEMINI_API_KEY=your_gemini_api_key_here
    GEMINI_MODEL=gemini-1.5-mini
    ```

## Usage

1.  Place your FNOL documents (PDF or TXT) in the `data/raw` directory. Sample documents are already provided.
2.  Run the main script:
    ```bash
    python main.py
    ```
3.  The script will process each document and output the recommended route to the console. Detailed extraction and routing information will be saved in `results.json`.

## Sample Documents

The `data/raw` directory contains sample documents covering various scenarios:
- `ACORD-Automobile-Loss-Notice-12.05.16.pdf`: A standard blank ACORD form (routes to Manual Review due to missing fields).
- `fnol_fast_track.txt`: A standard claim under $25,000.
- `fnol_manual_review.txt`: A claim missing the initial estimate.
- `fnol_investigation_flag.txt`: A claim with suspicious keywords in the description.
- `fnol_specialist_queue.txt`: An injury-related claim.
