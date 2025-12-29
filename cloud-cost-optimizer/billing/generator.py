import os
import json
import requests
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
# Llama 3.1 is generally more stable for JSON than 3.0
MODEL = "meta-llama/Llama-3.1-8B-Instruct"
API_URL = "https://router.huggingface.co/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

def extract_json_array(text: str) -> list:
    """
    Uses Regex to find the first '[' and last ']' to extract 
    a valid JSON list from potentially messy LLM output.
    """
    try:
        # 1. Look for the largest block starting with [ and ending with ]
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if not match:
            raise ValueError("No JSON array brackets ([ ]) found in output.")
        
        json_str = match.group(0)

        # 2. Cleanup: Remove common LLM mistakes like trailing commas before closing bracket
        json_str = re.sub(r',\s*\]', ']', json_str)
        
        return json.loads(json_str)
    except Exception as e:
        print(f"Extraction Error: {e}")
        print(f"Raw text snippet: {text[:200]}...")
        return None

def generate_mock_billing(project_profile: dict) -> list:
    """
    Sends project data to LLM and returns a list of billing records.
    """
    prompt = f"""
Generate synthetic, cloud-agnostic billing data for this project:
{json.dumps(project_profile, indent=2)}

RULES:
1. Generate exactly 15 billing records.
2. Total cost must sum up to roughly {project_profile['budget_inr_per_month']} INR.
3. Use only cloud-agnostic names (e.g., 'Object Storage' instead of 'S3').
4. Output ONLY a JSON array. 

Format for each record:
{{
  "month": "2025-01",
  "service": "Compute",
  "resource_id": "vm-01",
  "region": "asia-south",
  "usage_type": "on-demand",
  "usage_quantity": 720,
  "unit": "hours",
  "cost_inr": 1200,
  "desc": "Main server"
}}
"""

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a data generator. Output ONLY a raw JSON array. No conversational text."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2, # Lower temperature = more reliable JSON
        "max_tokens": 2000
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=45)
        response.raise_for_status()
        
        output_text = response.json()["choices"][0]["message"]["content"]
        
        # Extract and parse
        records = extract_json_array(output_text)
        
        if records is None:
            raise ValueError("Failed to parse JSON from LLM output.")
            
        return records

    except requests.exceptions.HTTPError as e:
        print(f"API Error: {response.status_code} - {response.text}")
        raise e

if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # 1. Load the profile generated in the previous step
    try:
        with open("data/project_profile.json", "r") as f:
            profile = json.load(f)
        
        print(f"🚀 Generating billing for: {profile.get('name', 'Unknown Project')}...")
        
        # 2. Run Generation
        billing_records = generate_mock_billing(profile)
        
        # 3. Save Results
        with open("data/mock_billing.json", "w") as f:
            json.dump(billing_records, f, indent=2)
            
        print(f"✅ Success! Generated {len(billing_records)} records in data/mock_billing.json")

    except FileNotFoundError:
        print("❌ Error: data/project_profile.json not found. Run your extractor script first.")
    except Exception as e:
        print(f"❌ Billing generation failed: {e}")