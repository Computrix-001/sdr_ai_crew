def log_message(message: str) -> None:
    """Logs a message to the console."""
    print(f"[LOG] {message}")

def handle_error(error: Exception) -> None:
    """Handles errors by logging them."""
    print(f"[ERROR] {str(error)}")

def validate_email(email: str) -> bool:
    """Validates the format of an email address."""
    import re
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

def format_lead_data(lead: dict) -> dict:
    """Formats lead data for consistency."""
    return {
        'name': lead.get('name', '').strip(),
        'email': lead.get('email', '').strip().lower(),
        'company': lead.get('company', '').strip(),
        'score': lead.get('score', 0)
    }