import json
import re
import os
from typing import Dict, List, Any

class ClaimsAgent:
    def __init__(self):
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-mini")
        self.client = self._initialize_client()
        self.mandatory_fields = [
            "policy_number", "policyholder_name", "date_of_loss", 
            "claim_type", "initial_estimate"
        ]
        self.fraud_keywords = ["fraud", "inconsistent", "staged"]

    def _initialize_client(self):
        try:
            from google.genai import Client
        except ImportError as exc:
            raise ImportError(
                "Gemini support requires google-genai. Install it with: pip install google-genai"
            ) from exc

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY must be set. Add it to .env or set the environment variable."
            )

        return Client(api_key=api_key)

    def _build_prompt(self, messages: List[Dict[str, Any]]) -> str:
        formatted = []
        for message in messages:
            role = message.get("role", "user").upper()
            content = message.get("content", "")
            formatted.append(f"{role}:\n{content}")
        return "\n\n".join(formatted)

    def _send_request(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        prompt = self._build_prompt(messages)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        text = response.text.strip() if response.text else "{}"
        return json.loads(text)

    def extract_fields(self, content: str) -> Dict[str, Any]:
        """
        Extract fields from text content only.
        """
        if not isinstance(content, str):
            raise ValueError("Gemini mode supports only text input. Provide the extracted PDF text or TXT content.")

        prompt = f"""
        Extract the following fields from the insurance FNOL document text provided below. 
        Return the result ONLY as a JSON object. If a field is not found, use an empty string.

        Fields to extract:
        - policy_number
        - policyholder_name
        - effective_dates
        - date_of_loss
        - time_of_loss
        - location
        - description
        - claimant
        - third_parties
        - contact_details
        - asset_type
        - asset_id
        - estimated_damage
        - claim_type
        - attachments
        - initial_estimate

        Document Text:
        {content}
        """
        messages = [
            {"role": "system", "content": "You are a helpful assistant that extracts structured data from insurance documents."},
            {"role": "user", "content": prompt}
        ]

        extracted = self._send_request(messages)
        flattened = {}
        for k, v in extracted.items():
            flattened[k] = str(v) if isinstance(v, dict) else v
        return flattened

    def validate_fields(self, fields: Dict[str, Any]) -> List[str]:
        missing = []
        for field in self.mandatory_fields:
            val = fields.get(field)
            if not val or str(val).strip().lower() in ["", "n/a", "none", "unknown", "{}"]:
                missing.append(field)
        return missing

    def route_claim(self, fields: Dict[str, Any], missing_fields: List[str]) -> Dict[str, str]:
        if missing_fields:
            return {
                "route": "Manual Review",
                "reasoning": f"Missing mandatory fields: {', '.join(missing_fields)}"
            }

        description = str(fields.get("description", "")).lower()
        if any(keyword in description for keyword in self.fraud_keywords):
            return {
                "route": "Investigation Flag",
                "reasoning": "Description contains suspicious keywords indicating potential fraud."
            }

        if str(fields.get("claim_type", "")).lower() == "injury":
            return {
                "route": "Specialist Queue",
                "reasoning": "Claim type is 'injury', requiring specialized handling."
            }

        estimate_str = str(fields.get("initial_estimate", "0"))
        estimate = self._parse_currency(estimate_str)

        if estimate < 25000:
            return {
                "route": "Fast-track",
                "reasoning": f"Estimated damage ({estimate_str}) is below the $25,000 threshold."
            }

        return {
            "route": "Standard Workflow",
            "reasoning": "Claim meets all criteria for standard processing."
        }

    def _parse_currency(self, value: str) -> float:
        if not value or str(value).lower() in ["n/a", "none", "unknown"]:
            return 0.0
        clean_value = re.sub(r'[^\d.]', '', str(value))
        try:
            return float(clean_value)
        except ValueError:
            return 0.0

    def process_claim(self, content: str) -> Dict[str, Any]:
        extracted_fields = self.extract_fields(content)
        missing_fields = self.validate_fields(extracted_fields)
        routing = self.route_claim(extracted_fields, missing_fields)

        return {
            "extractedFields": extracted_fields,
            "missingFields": missing_fields,
            "recommendedRoute": routing["route"],
            "reasoning": routing["reasoning"]
        }
