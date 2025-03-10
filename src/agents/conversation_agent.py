import os
from typing import Dict, List
from openai import AzureOpenAI

class ConversationAgent:
    def __init__(self):
        """Initialize ConversationAgent with Azure OpenAI client"""
        try:
            # Try with new CrewAI format first
            if os.getenv("AZURE_API_KEY") and os.getenv("AZURE_API_BASE"):
                self.client = AzureOpenAI(
                    api_key=os.getenv("AZURE_API_KEY"),
                    api_version=os.getenv("AZURE_API_VERSION"),
                    azure_endpoint=os.getenv("AZURE_API_BASE")
                )
            # Fall back to legacy format
            elif os.getenv("AZURE_OPENAI_API_KEY") and os.getenv("AZURE_OPENAI_ENDPOINT"):
                self.client = AzureOpenAI(
                    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
                )
            else:
                raise ValueError("Azure OpenAI credentials not found in environment variables")
        except Exception as e:
            print(f"Azure OpenAI initialization failed: {str(e)}")
            raise
        
    def handle_response(self, email_thread: List[str], lead_info: Dict) -> str:
        """Generate appropriate response based on email thread context"""
        context = "\n".join([
            f"Lead Info:",
            f"Company: {lead_info['company_name']}",
            f"Analysis: {lead_info.get('analysis', '')}",
            f"\nEmail Thread:",
            *email_thread
        ])

        response = self.client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "You are an AI sales development representative."},
                {"role": "user", "content": context}
            ],
            max_tokens=500
        )

        return response.choices[0].message.content.strip()

    def classify_intent(self, message: str) -> str:
        """Classify the intent of incoming messages"""
        response = self.client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "Classify the intent as: Interest, Objection, Question, Not Interested, or Meeting Request"},
                {"role": "user", "content": message}
            ],
            max_tokens=50
        )

        return response.choices[0].message.content.strip()