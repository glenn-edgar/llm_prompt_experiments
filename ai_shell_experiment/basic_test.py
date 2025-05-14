from openai import OpenAI
import os

# Fetch the API key from the environment
api_key = os.getenv("XAI_API_KEY")
if not api_key:
    raise ValueError("XAI_API_KEY not set. Run 'export XAI_API_KEY=your_key' in your terminal.")

# Initialize the client with xAI's API endpoint
client = OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1"
)

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

# Function to get Grok's response
def get_grok_response(prompt):
    try:
        response = client.chat.completions.create(
            model="grok-beta",  # Adjust if the model name changes (check console.x.ai)
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,     # Limit response length (adjust as needed)
            temperature=0.7     # Controls creativity
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error from Grok: {str(e)}"

# Main execution
if __name__ == "__main__":
    try:
        # Read the input from test.txt
        input_text = read_input_file()
        #print("Input from test.txt:", input_text)

        # Get and print Grok's response
        grok_response = get_grok_response(input_text)
        print("Grok's response:", grok_response)
    except Exception as e:
        print(f"Error: {str(e)}")
