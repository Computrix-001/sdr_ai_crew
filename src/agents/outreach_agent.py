from azure.communication.email import EmailClient
import pandas as pd
import os
from typing import Dict, List, Optional
from openai import AzureOpenAI
from datetime import datetime
import time

class RateLimiter:
    def __init__(self, max_requests: int = 50, time_window: int = 60):
        self.max_requests = max_requests  # requests per time window
        self.time_window = time_window  # time window in seconds
        self.requests = []
        
    def can_send(self) -> bool:
        """Check if we can send another email"""
        now = time.time()
        
        # Remove old requests
        self.requests = [req for req in self.requests 
                        if req > now - self.time_window]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False

class OutreachAgent:
    def __init__(self):
        """Initialize OutreachAgent with enhanced error handling"""
        try:
            # Initialize Azure Communication Services
            self._init_email_client()
            
            # Initialize Azure OpenAI
            self._init_openai_client()
            
            # Initialize Rate Limiter
            self.rate_limiter = RateLimiter(max_requests=50, time_window=60)
            
            print("✅ OutreachAgent initialized successfully")
            
        except Exception as e:
            print(f"❌ OutreachAgent initialization failed: {str(e)}")
            raise

    def _init_email_client(self):
        """Initialize Azure Communication Services email client"""
        self.connection_string = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING")
        if not self.connection_string:
            raise ValueError("AZURE_COMMUNICATION_CONNECTION_STRING not found")
            
        self.sender = os.getenv("AZURE_COMMUNICATION_SENDER_EMAIL")
        if not self.sender:
            raise ValueError("AZURE_COMMUNICATION_SENDER_EMAIL not found")
            
        self.email_client = EmailClient.from_connection_string(self.connection_string)

    def _init_openai_client(self):
        """Initialize Azure OpenAI client"""
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_API_KEY"),
            api_version=os.getenv("AZURE_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_API_BASE")
        )
        self.deployment_name = "gama"

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
                    
                success = self.send_email_with_retry(
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

    def send_email_with_retry(self, recipient: str, subject: str, content: str, 
                            max_retries: int = 3, retry_delay: int = 2) -> bool:
        """Send email with retry mechanism and better error handling"""
        for attempt in range(max_retries):
            try:
                # Validate email content
                if not self._validate_email(recipient, subject, content):
                    raise ValueError("Invalid email parameters")

                # Create email message
                message = EmailMessage(
                    sender=self.sender,
                    subject=subject,
                    body=content,  # Plain text content
                    recipients=[EmailAddress(email=recipient)]  # List of recipients
                )

                # Send email
                poller = self.email_client.begin_send(message)
                result = poller.result()
                
                print(f"✅ Email sent successfully to {recipient}")
                return True

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    print(f"❌ Failed to send email to {recipient} after {max_retries} attempts")
                    return False
                time.sleep(retry_delay ** attempt)  # Exponential backoff

    def send_email(self, recipient: str, subject: str, content: str) -> bool:
        """Public method to send emails with full error handling and logging"""
        try:
            # Log attempt
            print(f"\nAttempting to send email to: {recipient}")
            print(f"Subject: {subject}")
            
            # Validate inputs
            if not self._validate_email(recipient, subject, content):
                return False
                
            # Send with retry
            success = self.send_email_with_retry(
                recipient=recipient,
                subject=subject,
                content=content
            )
            
            if success:
                # Track the email
                status = self.track_email_status(recipient)
                print(f"Email tracked: {status}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            return False

    def _validate_email(self, recipient: str, subject: str, content: str) -> bool:
        """Validate email parameters"""
        if not recipient or not '@' in recipient:
            print("Invalid recipient email")
            return False
        if not subject or len(subject) < 2:
            print("Invalid subject")
            return False
        if not content or len(content) < 10:
            print("Invalid content")
            return False
        return True

    def _convert_to_html(self, content: str) -> str:
        """Convert plain text to HTML format"""
        paragraphs = content.split('\n\n')
        html_content = []
        for p in paragraphs:
            if p.strip():
                html_content.append(f"<p>{p.strip()}</p>")
        return "\n".join(html_content)

    def track_email_status(self, recipient: str) -> Dict:
        """Track email delivery status"""
        # Implementation depends on Azure Communication Services capabilities
        # This is a placeholder for future implementation
        return {
            "recipient": recipient,
            "status": "sent",
            "timestamp": datetime.now().isoformat()
        }

    def validate_template(self, template: Dict) -> bool:
        """Validate email template structure"""
        required_fields = ['subject', 'content']
        if not all(field in template for field in required_fields):
            print("Missing required template fields")
            return False
            
        # Check content length
        if len(template['content']) < 50:
            print("Email content too short")
            return False
            
        # Check for spam triggers
        spam_triggers = ['urgent', 'guarantee', 'free', 'winner']
        content_lower = template['content'].lower()
        for trigger in spam_triggers:
            if trigger in content_lower:
                print(f"Found spam trigger word: {trigger}")
                return False
            
        return True