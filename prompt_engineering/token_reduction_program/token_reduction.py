import re
import nltk
import os
import sys
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

def ensure_nltk_resources():
    """Ensure NLTK resources are available and properly configured."""
    resources = ['punkt', 'stopwords']
    
    # Print NLTK data paths for debugging
    print("NLTK is looking for resources in these directories:")
    for path in nltk.data.path:
        print(f" - {path}")
    
    # Check if resources exist in any of the paths
    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
            print(f"✓ Resource '{resource}' is available")
        except LookupError:
            print(f"✗ Resource '{resource}' not found, attempting to download...")
            try:
                nltk.download(resource, quiet=False)
                print(f"  Downloaded '{resource}' successfully")
            except Exception as e:
                print(f"  Failed to download '{resource}': {e}")
    
    # Special handling for punkt_tab issue
    punkt_path = None
    for path in nltk.data.path:
        potential_path = os.path.join(path, 'tokenizers', 'punkt')
        if os.path.exists(potential_path):
            punkt_path = potential_path
            break
    
    if punkt_path:
        # Ensure punkt_tab/english exists
        punkt_tab_dir = os.path.join(punkt_path, 'PY3', 'english.pickle')
        if not os.path.exists(punkt_tab_dir):
            print("Warning: punkt installation may be incomplete.")
            print(f"Checked for file at: {punkt_tab_dir}")
            print("This might cause issues with sentence tokenization.")

def reduce_token_count(text, aggressive=False):
    """
    Reduce the token count of text meant for LLMs while preserving core meaning.
    
    Args:
        text (str): The input text to be reduced
        aggressive (bool): Whether to apply more aggressive reduction techniques
        
    Returns:
        str: The reduced text
    """
    # Initial preprocessing
    text = text.strip()
    
    # Common redundant phrases to replace
    redundant_phrases = {
        r'\b(in order to)\b': 'to',
        r'\b(a number of|numerous|several|many|multiple)\b': 'many',
        r'\b(for the purpose of)\b': 'for',
        r'\b(in the event that)\b': 'if',
        r'\b(due to the fact that)\b': 'because',
        r'\b(at this point in time|at the present time)\b': 'now',
        r'\b(it is (important|necessary) to note that)\b': '',
        r'\b(in the process of)\b': 'while',
        r'\b(on a (daily|regular) basis)\b': 'daily',
        r'\b(in spite of the fact that)\b': 'although',
        r'\b(in the near future)\b': 'soon',
        r'\b(it should be noted that)\b': '',
        r'\b(as a matter of fact)\b': '',
        r'\b(the vast majority of)\b': 'most',
        r'\b(in my (humble|honest) opinion)\b': '',
        r'\b(for all intents and purposes)\b': '',
        r'\b(at the end of the day)\b': '',
        r'\b(needless to say)\b': '',
        r'\b(each and every)\b': 'each',
        r'\b(as far as I am concerned)\b': '',
        r'\b(as a general rule)\b': 'generally',
        r'\b(take into consideration)\b': 'consider',
        r'\b(in view of the fact that)\b': 'since',
        r'\b(in the final analysis)\b': 'finally',
        r'\b(in actual fact)\b': '',
        r'\b(absolutely essential)\b': 'essential',
        r'\b(basic fundamentals)\b': 'basics',
        r'\b(completely eliminate)\b': 'eliminate',
        r'\b(new innovation)\b': 'innovation',
        r'\b(personal opinion)\b': 'opinion',
        r'\b(past history)\b': 'history',
        r'\b(advance planning)\b': 'planning',
        r'\b(unexpected surprise)\b': 'surprise',
        r'\b(future plans)\b': 'plans',
        r'\b(please be advised that)\b': '',
        r'\b(the reason why is that)\b': 'because',
        r'\b(would like to)\b': 'want to',
        r'\b(I would like to)\b': 'I want to',
    }
    
    # Apply phrase replacements
    for pattern, replacement in redundant_phrases.items():
        text = re.sub(pattern, replacement, text)
    
    try:
        # Sentence-level processing using a more cautious approach
        try:
            sentences = sent_tokenize(text)
        except LookupError:
            # Fallback to simple sentence splitting if NLTK fails
            print("Warning: NLTK sentence tokenization failed, using simple fallback.")
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text)]
        
        processed_sentences = []
        
        try:
            stop_words = set(stopwords.words('english'))
            # Keep some important stop words
            for word in ['not', 'no', 'nor', 'but']:
                if word in stop_words:
                    stop_words.remove(word)
        except LookupError:
            # Fallback with a minimal set of common English stopwords
            print("Warning: NLTK stopwords not available, using minimal fallback set.")
            stop_words = set(['a', 'an', 'the', 'and', 'or', 'but', 'if', 'then', 
                             'while', 'of', 'at', 'by', 'for', 'with', 'about', 
                             'against', 'between', 'into', 'through', 'during', 
                             'before', 'after', 'above', 'below', 'to', 'from', 
                             'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under'])
        
        for sentence in sentences:
            # Skip sentences that are likely to be redundant explanations or filler
            if re.search(r'\b(as mentioned earlier|as stated above|as discussed|to reiterate)\b', sentence.lower()):
                continue
                
            # Process sentence
            try:
                words = word_tokenize(sentence)
            except LookupError:
                # Fallback to simple word splitting
                words = re.findall(r'\b\w+\b', sentence)
            
            # Remove some stop words if aggressive mode is enabled
            if aggressive:
                words = [word for word in words if word.lower() not in stop_words or word in ['not', 'no']]
            
            # Rejoin the words
            processed_sentence = ' '.join(words)
            
            # Fix spacing around punctuation
            processed_sentence = re.sub(r'\s+([,.!?:;])', r'\1', processed_sentence)
            
            processed_sentences.append(processed_sentence)
        
        # Join sentences
        reduced_text = ' '.join(processed_sentences)
    except Exception as e:
        print(f"Warning: Error during text processing: {e}")
        print("Falling back to basic reduction...")
        # Fallback to simpler processing if NLTK fails
        reduced_text = text
        for pattern, replacement in redundant_phrases.items():
            reduced_text = re.sub(pattern, replacement, reduced_text)
    
    # Additional fixes for common patterns
    # Remove repeated spaces
    reduced_text = re.sub(r'\s+', ' ', reduced_text)
    
    # Convert contractions to shorter forms (if not already done)
    contractions = {
        r'\b(it is)\b': "it's",
        r'\b(do not)\b': "don't",
        r'\b(cannot)\b': "can't",
        r'\b(I am)\b': "I'm",
        r'\b(they are)\b': "they're",
        r'\b(we are)\b': "we're",
        r'\b(you are)\b': "you're",
        r'\b(will not)\b': "won't",
        r'\b(they have)\b': "they've",
        r'\b(we have)\b': "we've",
        r'\b(I have)\b': "I've",
        r'\b(you have)\b': "you've",
        r'\b(would have)\b': "would've",
        r'\b(could have)\b': "could've",
        r'\b(should have)\b': "should've",
    }
    
    for pattern, replacement in contractions.items():
        reduced_text = re.sub(pattern, replacement, reduced_text)
    
    return reduced_text.strip()

def simple_word_count(text):
    """Simple word count fallback that doesn't rely on NLTK."""
    return len(re.findall(r'\b\w+\b', text))

def main(filename=None):
    """
    Main function that processes text from a file or user input.
    
    Args:
        filename (str, optional): Path to the input file. If None, get input from user.
    """
    print("LLM Text Token Reducer")
    print("----------------------")
    
    # Check NLTK resources at the beginning
    ensure_nltk_resources()
    
    # Get text either from file or user input
    if filename:
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                text = file.read()
            print(f"Read input from file: {filename}")
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return
        except Exception as e:
            print(f"Error reading file: {e}")
            return
    else:
        print("Enter your text (type 'END' on a new line when finished):")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        text = "\n".join(lines)
    
    # Get reduction mode
    aggressive_mode = input("Use aggressive reduction? (y/n): ").lower() == 'y'
    
    # Process text
    reduced_text = reduce_token_count(text, aggressive=aggressive_mode)
    
    # Display results with fallback for token counting
    try:
        original_tokens = len(word_tokenize(text))
        reduced_tokens = len(word_tokenize(reduced_text))
    except:
        # Simple fallback if NLTK tokenization fails
        print("Note: Using simple word count as fallback (NLTK tokenization unavailable)")
        original_tokens = simple_word_count(text)
        reduced_tokens = simple_word_count(reduced_text)
    
    reduction_percent = round((1 - reduced_tokens / original_tokens) * 100, 2) if original_tokens > 0 else 0
    
    print("\nOriginal text length:", original_tokens, "tokens")
    print("Reduced text length:", reduced_tokens, "tokens")
    print("Reduction:", reduction_percent, "%")
    
    print("\n--- Reduced Text ---")
    print(reduced_text)
    
    # Optionally save the output
    save_option = input("\nSave reduced text to file? (y/n): ").lower()
    if save_option == 'y':
        output_filename = input("Enter output filename: ")
        try:
            with open(output_filename, 'w', encoding='utf-8') as file:
                file.write(reduced_text)
            print(f"Reduced text saved to {output_filename}")
        except Exception as e:
            print(f"Error saving file: {e}")

if __name__ == "__main__":
    main("input.txt")
