import os
import tiktoken
import openai

# ——— Configuration ———
# Install dependencies with: pip install openai tiktoken
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4"   # or another chat-capable model

# ——— Helper: count tokens via tiktoken ———
def count_tokens(text: str, model: str = MODEL) -> int:
    """Return number of tokens in `text` for given `model`."""
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

# ——— Core: compress text ———
def compress_text(text: str, model: str = MODEL, max_retries: int = 3) -> str:
    """
    Ask the LLM to rewrite `text` as concisely as possible while preserving meaning.
    Returns the compressed text.
    """
    system_prompt = (
        "You are a text-compression assistant. "
        "Given an input, produce a semantically equivalent output "
        "that minimizes token usage. Be concise."
    )
    user_prompt = f"Compress the following text:\n\n'''{text}'''"
    
    for attempt in range(1, max_retries+1):
        try:
            resp = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt}
                ],
                temperature=0.0,
            )
            return resp.choices[0].message.content.strip()
        except openai.error.OpenAIError as e:
            if attempt == max_retries:
                raise
            else:
                print(f"API error (attempt {attempt}): {e}. Retrying…")

# ——— CLI / Example usage ———
if __name__ == "__main__":
    import argparse, sys
    
    parser = argparse.ArgumentParser(
        description="Compress text to reduce LLM token usage while preserving meaning."
    )
    parser.add_argument("infile", nargs="?", type=argparse.FileType('r'),
                        default=sys.stdin,
                        help="Path to input text file (or STDIN)")
    parser.add_argument("--model", default=MODEL,
                        help="OpenAI model to use for compression")
    args = parser.parse_args()
    
    original = args.infile.read().strip()
    print(f"Original token count: {count_tokens(original, args.model)}")
    
    compressed = compress_text(original, model=args.model)
    print("\n--- Compressed Output ---\n")
    print(compressed)
    print(f"\nCompressed token count: {count_tokens(compressed, args.model)}")
