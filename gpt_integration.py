import openai
import os
from dotenv import load_dotenv
import time
from openai.error import RateLimitError
import logging  # Import logging for error tracking

# Configure logging
logging.basicConfig(level=logging.ERROR, filename='error_log.txt', 
                    format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

def generate_gpt_response(prompt):
    retries = 5
    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}],
                max_tokens=150
            )
            return response
        except RateLimitError as e:
            logging.error(f"RateLimitError: {e} - Attempt {attempt + 1}")  # Log the error
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print("Error: Rate limit exceeded. Please try again later.")  # User-friendly message
                return None  # Return None to indicate failure
        except Exception as e:  # Catch all other exceptions
            logging.error(f"OpenAI API error: {e}")  # Log the error
            print("An error occurred while communicating with OpenAI. Please check the logs for more details.")
            return None  # Return None to indicate failure

# Example usage
if __name__ == "__main__":
    prompt = "What is the best strategy for buying and selling cryptocurrency?"
    response = generate_gpt_response(prompt)
    
    if response:
        print(f"GPT Response: {response}")
    else:
        print("Failed to get a response from GPT.") 