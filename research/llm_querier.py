import json
import re
import time
from openai import OpenAI

# Initialize OpenAI client (reads OPENAI_API_KEY from environment)
client = OpenAI()

def load_prompts(filepath="prompts.json"):
    """Load prompt dataset"""
    with open(filepath, "r") as f:
        return json.load(f)

def extract_package_names(text):
    """
    Extract package names from LLM response.
    Looks for: import X, from X import, pip install X, require('X')
    """
    packages = set()
    
    # Python imports: import X, from X import
    python_patterns = [
        r'^\s*(?:from|import)\s+([a-zA-Z0-9_\-\.]+)',
        r'pip\s+install\s+([a-zA-Z0-9_\-\.]+)',
        r'requires=\[([^\]]+)\]',
    ]
    
    # JavaScript requires: require('X'), import X from 'X'
    js_patterns = [
        r'require\([\'"]([a-zA-Z0-9_\-\.]+)[\'"]\)',
        r'import\s+\w+\s+from\s+[\'"]([a-zA-Z0-9_\-\.]+)[\'"]',
        r'npm\s+install\s+([a-zA-Z0-9_\-\./@]+)',
    ]
    
    all_patterns = python_patterns + js_patterns
    
    for pattern in all_patterns:
        matches = re.findall(pattern, text, re.MULTILINE)
        for match in matches:
            # Clean up and normalize
            pkg = match.strip().strip("'\"").split()[0]
            if pkg and not pkg.startswith("http"):
                packages.add(pkg)
    
    return list(packages)

def query_llm(prompt, model="gpt-4o-mini"):
    """Query OpenAI and return response"""
    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": f"Provide Python/JavaScript code for: {prompt}\n\nInclude package imports at the top."
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error querying LLM: {e}")
        return ""

def run_discovery(prompts_file="prompts.json", output_file="llm_responses.json"):
    """Run LLM querying and package extraction"""
    prompts = load_prompts(prompts_file)
    results = {
        "model": "gpt-4o-mini",
        "total_prompts": 0,
        "responses": []
    }
    
    for category, prompt_list in prompts.items():
        print(f"\n[*] Processing category: {category}")
        for prompt_obj in prompt_list[:2]:  # Only first 2 prompts per category for testing
            prompt_id = prompt_obj["id"]
            prompt_text = prompt_obj["prompt"]
            
            print(f"  Querying: {prompt_id}...", end=" ", flush=True)
            response = query_llm(prompt_text)
            packages = extract_package_names(response)
            
            results["responses"].append({
                "id": prompt_id,
                "category": category,
                "prompt": prompt_text,
                "packages": packages,
                "response_snippet": response[:200]
            })
            
            results["total_prompts"] += 1
            print(f"Found {len(packages)} packages")
            time.sleep(1)  # Rate limiting
    
    # Save results
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[+] Results saved to {output_file}")
    return results

if __name__ == "__main__":
    run_discovery()