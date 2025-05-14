from openai import OpenAI
import os
import json

# Fetch the API key from the environment
api_key = os.getenv("XAI_API_KEY")
if not api_key:
    raise ValueError("XAI_API_KEY not set. Run 'export XAI_API_KEY=your_key' in your terminal.")

# Initialize the client with xAI's API endpoint
client = OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1"
)

# Predefined structure (you can move this to a separate file if preferred)
default_structure = {
    "verbs": {
        "Paint": {"objects": ["house", "car"], "adverbs": ["quickly", "carefully"]},
        "Run": {"objects": ["race", "track"], "adverbs": ["fast", "slowly"]}
    },
    "objects": {
        "house": ["red", "big"],
        "car": ["blue", "small"],
        "race": ["long", "short"],
        "track": ["wide", "narrow"]
    }
}

# Instructions for Grok (condensed version of your earlier spec)
instructions = """
Parse the input sentence in the form 'verb object [adverb/adjective]' and return only a JSON structure. 
- Verify terms against the provided structure.
- Correct misspelled words to the closest supported term.
- Include invalid attributes in the output with 'match' fields to flag errors.
- Output format: 
  {
    "sentence": "<original>",
    "verb": {"text": "<verb>", "attributes": {"adverb": "<adverb>"} or {}, "match": true/false},
    "object": {"text": "<object phrase>", "noun": "<noun>", "attributes": {"adjective": "<adjective>"} or {}, "match": true/false},
    "words": ["<word1>", "<word2>", "<word3>"],
    "length": <int>,
    "match": true/false
  }
Use the provided structure or the default if none is given.
"""

# Function to read input from test.txt
def read_input_file(filename="test.txt"):
    try:
        with open(filename, "r") as file:
            content = file.read().strip()
            if not content:
                raise ValueError("The file test.txt is empty.")
            return content
    except FileNotFoundError:
        raise FileNotFoundError("test.txt not found. Please create the file with your input.")
    except Exception as e:
        raise Exception(f"Error reading test.txt: {str(e)}")

# Function to get Grok's JSON response
def get_grok_response(sentence, structure=default_structure):
    try:
        # Construct the prompt with instructions, structure, and input
        prompt = f"{instructions}\nStructure:\n{json.dumps(structure, indent=2)}\nInput sentence:\n{sentence}\nReturn only the JSON structure."
        
        response = client.chat.completions.create(
            model="grok-beta",  # Adjust if the model name changes
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.0  # Set to 0 for deterministic output
        )
        # Extract and parse the response as JSON
        response_text = response.choices[0].message.content.strip()
        return json.loads(response_text)  # Expecting Grok to return pure JSON
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from Grok", "raw": response_text}
    except Exception as e:
        return {"error": f"Error from Grok: {str(e)}"}

# Main execution
if __name__ == "__main__":
    try:
        # Read the input from test.txt
        input_text = read_input_file()
        #print("Input from test.txt:", input_text)

        # Get and print Grok's JSON response
        grok_response = get_grok_response(input_text)
        print("Grok's response:")
        print(json.dumps(grok_response, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")

