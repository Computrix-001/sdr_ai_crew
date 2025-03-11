from openai import AzureOpenAI
from dotenv import load_dotenv
import os

def test_connection():
    """Test Azure OpenAI connection with detailed debugging"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Print configuration for debugging
        print("\nConfiguration:")
        print(f"API Key: {os.getenv('AZURE_API_KEY')[:5]}...")  # Only show first 5 chars
        print(f"Endpoint: {os.getenv('AZURE_API_BASE')}")
        print(f"API Version: 2024-07-18-preview")
        print(f"Deployment: gama")
        
        # Initialize the client
        client = AzureOpenAI(
            api_key=os.getenv('AZURE_API_KEY'),
            api_version="2024-07-18-preview",
            azure_endpoint=os.getenv('AZURE_API_BASE')
        )
        
        print("\nTesting connection...")
        
        # Test completion
        completion = client.chat.completions.create(
            model="gama",  # deployment name
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'hello' for testing"}
            ],
            temperature=0,
            max_tokens=10
        )
        
        print("\nConnection successful! ✅")
        print(f"Response: {completion.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"\nConnection failed! ❌")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        if hasattr(e, 'response'):
            print(f"\nResponse status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return False

if __name__ == "__main__":
    test_connection() 