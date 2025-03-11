from openai import AzureOpenAI
from dotenv import load_dotenv
import os

def test_azure_deployment():
    """Test Azure OpenAI deployment connection"""
    try:
        # Load environment variables
        load_dotenv()
        
        print("Testing Azure OpenAI Connection...")
        print(f"Deployment Name: {os.getenv('AZURE_OPENAI_DEPLOYMENT')}")
        print(f"API Version: {os.getenv('AZURE_API_VERSION')}")
        print(f"Endpoint: {os.getenv('AZURE_API_BASE')}")
        
        # Initialize the client
        client = AzureOpenAI(
            api_key=os.getenv('AZURE_API_KEY'),
            api_version="2024-07-18-preview",  # Hardcode the correct version
            azure_endpoint=os.getenv('AZURE_API_BASE')
        )

        # Test the deployment
        response = client.chat.completions.create(
            model="gama",  # Use the deployment name directly
            messages=[{"role": "system", "content": "Test connection"}],
            max_tokens=5
        )
        
        print("\nConnection Successful! ✅")
        print(f"Response: {response}")
        return True
        
    except Exception as e:
        print(f"\nConnection Failed! ❌")
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_azure_deployment()