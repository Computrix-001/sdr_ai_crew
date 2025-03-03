# SDR AI Crew System

## Overview
The SDR AI Crew System is a multi-agent system designed for automated sales development using the Crew AI framework. It leverages various AI capabilities and APIs to streamline lead generation, research, outreach, and conversation handling.

## Project Structure
```
sdr-ai-crew-system
├── src
│   ├── agents
│   │   ├── __init__.py
│   │   └── lead_generation_agent.py
│   ├── tools
│   │   ├── __init__.py
│   │   └── serp_api.py
│   ├── config
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── utils
│   │   ├── __init__.py
│   │   └── helpers.py
│   ├── __init__.py
│   └── main.py
├── .env
├── requirements.txt
└── README.md
```

## Features
1. **Automated Lead Generation**: Utilizes the SERP API for web scraping to gather potential leads.
2. **Lead Research & Profiling**: Profiles and scores leads to prioritize outreach efforts.
3. **Email Outreach**: Automates email communication using Azure Communication Services, including follow-ups.
4. **24/7 Conversation Handling**: Manages ongoing conversations with leads, providing context-aware responses.

## Technology Stack
- **Programming Language**: Python 3.9+
- **Framework**: Crew AI Framework
- **APIs**: Azure OpenAI, Azure Communication Services, SERP API

## Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   cd sdr-ai-crew-system
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Create a `.env` file in the root directory and add your API keys and connection strings as specified in the provided `.env` template.

## Usage
To run the application, execute the following command:
```
python src/main.py
```

## Contribution
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.