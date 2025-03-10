from azure.communication.email import EmailClient
import pandas as pd
import os
from typing import Dict, List
from openai import AzureOpenAI
from datetime import datetime

class OutreachAgent:
    def __init__(self):
        """Initialize OutreachAgent with necessary clients and configurations"""
        # Initialize deployment name first
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        if not self.deployment_name:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT not found in environment variables")
        
        print(f"Using deployment name: {self.deployment_name}")  # Debug print

        # Initialize email client
        self.connection_string = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING")
        if not self.connection_string:
            raise ValueError("AZURE_COMMUNICATION_CONNECTION_STRING not found in environment variables")
        
        self.email_client = EmailClient.from_connection_string(self.connection_string)
        self.sender = os.getenv("AZURE_COMMUNICATION_SENDER_EMAIL")
        if not self.sender:
            raise ValueError("AZURE_COMMUNICATION_SENDER_EMAIL not found in environment variables")
            
        # Initialize Azure OpenAI client
        try:
            if os.getenv("AZURE_API_KEY") and os.getenv("AZURE_API_BASE"):
                self.client = AzureOpenAI(
                    api_key=os.getenv("AZURE_API_KEY"),
                    api_version=os.getenv("AZURE_API_VERSION", "2024-02-15-preview"),
                    azure_endpoint=os.getenv("AZURE_API_BASE")
                )
                
                # Test the deployment
                try:
                    test_response = self.client.chat.completions.create(
                        model=self.deployment_name,
                        messages=[
                            {"role": "system", "content": "Test deployment connection"}
                        ],
                        max_tokens=5
                    )
                    print("Successfully connected to Azure OpenAI deployment")
                except Exception as e:
                    print(f"Deployment test failed: {str(e)}")
                    if '404' in str(e):
                        raise ValueError(f"Azure OpenAI deployment '{self.deployment_name}' not found. Please verify the deployment name in Azure Portal.")
                    raise e
                
            else:
                raise ValueError("Azure OpenAI credentials not found in environment variables")
                
        except Exception as e:
            print(f"Azure OpenAI initialization failed: {str(e)}")
            raise

    def process_leads(self, analyzed_leads: List[Dict]) -> List[Dict]:
        """Process and send emails to analyzed leads"""
        results = []
        if not analyzed_leads:
            print("No leads to process")
            return results

        total_leads = len(analyzed_leads)
        print(f"\nProcessing {total_leads} leads for email outreach...")

        for index, lead in enumerate(analyzed_leads, 1):
            try:
                company_name = lead.get('company_name', 'Unknown Company')
                print(f"Attempting to send email to: {lead.get('contact_email', 'No email')}")
                
                if not lead.get('contact_email'):
                    print(f"No email address found for {company_name}")
                    continue
                
                email_content = self.generate_email(lead)
                if not email_content:
                    print(f"Failed to generate email content for {company_name}")
                    continue
                    
                success = self.send_email(
                    recipient=lead['contact_email'],
                    subject=email_content['subject'],
                    content=email_content['content']
                )
                
                results.append({
                    **lead,
                    'email_sent': success,
                    'email_content': email_content,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Error processing lead {company_name}: {str(e)}")
                results.append({
                    **lead,
                    'email_sent': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
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
            # Extract lead information
            company_name = lead.get('company_name', 'your company')
            contact_name = lead.get('contact_name', 'Decision Maker')
            industry = lead.get('industry', 'your industry')
            research_data = lead.get('research_data', '')
            value_prop = lead.get('value_prop', '')
            tone = lead.get('tone', 'Professional')
            email_length = lead.get('email_length', 'Medium')
            
            prompt = f"""
            Create a highly personalized B2B sales email using this information:
            
            COMPANY INFO:
            Company: {company_name}
            Contact: {contact_name}
            Industry: {industry}
            
            RESEARCH INSIGHTS:
            {research_data}
            
            CUSTOMIZATION:
            Tone: {tone}
            Length: {email_length}
            Value Proposition: {value_prop}
            
            GUIDELINES:
            1. Keep it concise and focused
            2. Highlight specific value propositions
            3. Include a clear call to action
            4. Maintain the specified tone
            5. Adapt length based on the {email_length} preference
            """

            try:
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=[
                        {"role": "system", "content": "You are an expert SDR crafting personalized emails."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=800,
                    temperature=0.7
                )

                email_content = response.choices[0].message.content.strip()
                
                # Generate subject line
                subject_prompt = f"""
                Create a compelling subject line for a B2B sales email to {company_name}.
                Industry: {industry}
                Keep it short, specific, and engaging.
                """
                
                subject_response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=[
                        {"role": "system", "content": "Create short, engaging email subject lines."},
                        {"role": "user", "content": subject_prompt}
                    ],
                    max_tokens=50,
                    temperature=0.7
                )
                
                subject_line = subject_response.choices[0].message.content.strip()
                
                return {
                    "subject": subject_line,
                    "content": email_content
                }
            except Exception as api_error:
                if '404' in str(api_error):
                    print(f"Error: Azure OpenAI deployment '{self.deployment_name}' not found")
                raise api_error
                
        except Exception as e:
            print(f"Error generating email content: {str(e)}")
            return None

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

            print(f"Sending email to: {recipient}")
            poller = self.email_client.begin_send(message)
            result = poller.result()
            print(f"✓ Email sent successfully to {recipient}")
            return True
            
        except Exception as e:
            print(f"✗ Error sending email to {recipient}")
            print(f"Error details: {str(e)}")
            return False