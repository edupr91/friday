import requests
import json
import os
import sys
from rich.console import Console
from rich.markdown import Markdown

# Retrieve the API key from the environment variable
api_key = os.environ.get("GEMINI_API_KEY")

# Define the Gemini model and API endpoint
gemini_model = "gemini-2.5-flash-lite"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={api_key}"

def call_gemini_api(prompt):
    """
    Calls the Gemini API with the given prompt and retrieves the generated content.

    Args:
        prompt (str): The input text prompt to send to the Gemini API.

    Returns:
        str: The generated content from the API response, or None if an error occurs.
    """
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    try:
        # Send a POST request to the Gemini API
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        # Extract the generated text content from the API response
        text_content = data['candidates'][0]['content']['parts'][0]['text']
        return text_content.strip()
    except requests.exceptions.HTTPError as err_http:
        # Handle HTTP errors
        print(f"HTTP Error: {err_http}")
        print(f"Response Body: {response.text}")
    except requests.exceptions.RequestException as err:
        # Handle other request-related errors
        print(f"An unexpected error occurred: {err}")
    except (KeyError, IndexError) as err_json:
        # Handle errors while parsing the JSON response
        print(f"Error parsing JSON response: {err_json}")
    return None

if __name__ == "__main__":
    # Check if the API key is set
    if not api_key:
        print("Please set the GEMINI_API_KEY environment variable.")
        sys.exit(1)
    # Ensure a prompt is provided as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python main.py <your prompt here>")
        sys.exit(1)
    # Combine command-line arguments into a single prompt string
    prompt_text = " ".join(sys.argv[1:])
    # Call the Gemini API with the provided prompt
    answer = call_gemini_api(prompt_text)
    console = Console()
    if answer:
        # Display the generated content using rich Markdown formatting
        console.print(Markdown(answer))
    else:
        # Display an error message if no valid answer is retrieved
        console.print("[red]Could not retrieve a valid answer.[/red]")