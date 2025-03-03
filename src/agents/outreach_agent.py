from azure.communication.email import EmailClient
import pandas as pd
import os
from typing import Dict, List
from openai import AzureOpenAI

class OutreachAgent:
    def __init__(self):
        """Initialize OutreachAgent with necessary clients and configurations"""
        self.connection_string = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING")
        if not self.connection_string:
            raise ValueError("AZURE_COMMUNICATION_CONNECTION_STRING not found in environment variables")
        
        self.email_client = EmailClient.from_connection_string(self.connection_string)
        self.sender = os.getenv("AZURE_COMMUNICATION_SENDER_EMAIL")
        if not self.sender:
            raise ValueError("AZURE_COMMUNICATION_SENDER_EMAIL not found in environment variables")
            
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
    
    def process_leads(self, analyzed_leads: List[Dict]) -> List[Dict]:
        """Process and send emails to analyzed leads"""
        results = []
        if not analyzed_leads:
            print("No leads to process")
            return results

        total_leads = len(analyzed_leads)
        print(f"\nProcessing {total_leads} leads for email outreach...")

        for index, lead in enumerate(analyzed_leads, 1):
            company_name = lead.get('company_name', 'Unknown Company')
            print(f"\n[{index}/{total_leads}] Processing: {company_name}")
            
            email_content = self.generate_email(lead)
            success = self.send_email(
                recipient=lead.get('contact_email'),
                subject=email_content['subject'],
                content=email_content['content']
            )
            
            results.append({
                **lead,
                'email_sent': success,
                'email_content': email_content,
                'timestamp': pd.Timestamp.now().isoformat()
            })

        # Print summary
        successful = sum(1 for r in results if r['email_sent'])
        print(f"\nOutreach Summary:")
        print(f"Total Processed: {total_leads}")
        print(f"Successfully Sent: {successful}")
        print(f"Failed: {total_leads - successful}")

        return results

    def generate_email(self, lead: Dict) -> Dict:
        """Generate personalized email content using Azure OpenAI"""
        try:
            research_data = lead.get('research_data', '')
            scoring_analysis = lead.get('scoring_analysis', '')
            
            prompt = f"""
            Create a highly personalized B2B sales email using this research:
            
            COMPANY INFO:
            Company: {lead.get('company_name', 'Unknown Company')}
            Contact: {lead.get('contact_name', 'Decision Maker')}
            Industry: {lead.get('industry', 'Unknown Industry')}
            Website: {lead.get('website', 'N/A')}
            
            RESEARCH INSIGHTS:
            {research_data}
            
            LEAD SCORING:
            {scoring_analysis}
            """

            response = self.client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                messages=[
                    {"role": "system", "content": "You are an expert SDR crafting personalized emails."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )

            email_content = response.choices[0].message.content.strip()
            
            return {
                "subject": f"Quick question about {lead.get('company_name', 'your company')}",
                "content": email_content
            }
        except Exception as e:
            print(f"Error generating email content: {e}")
            return {
                "subject": "Unable to generate email",
                "content": "Error generating personalized content"
            }

    def send_email(self, recipient: str, subject: str, content: str) -> bool:
        """Send email using Azure Communication Services"""
        try:
            if not recipient:
                print("No recipient email provided")
                return False
                
            message = {
                "content": {
                    "subject": subject,
                    "plainText": content,
                },
                "recipients": {
                    "to": [{"address": recipient}]
                },
                "senderAddress": self.sender
            }

            print(f"Attempting to send email to: {recipient}")
            poller = self.email_client.begin_send(message)
            result = poller.result()
            print(f"✓ Email sent successfully to {recipient}")
            return True
            
        except Exception as e:
            print(f"✗ Error sending email to {recipient}")
            print(f"Error details: {str(e)}")
            return False