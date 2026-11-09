# Aasara (ఆసరా) – Telugu Voice Guide to Government Schemes

## About the Project
Aasara is an AI-powered voice assistant that helps Telugu-speaking users discover government welfare schemes through natural voice conversations.

Users can ask questions in Telugu or Hindi, answer follow-up questions, and hear information about potentially eligible schemes.

## Key Features
- Telugu and Hindi voice interaction.
- Speech-to-text using Gnani Prisma.
- AI-powered query understanding using Google Gemini.
- Eligibility checking against a dataset of 9 central and Telangana schemes.
- Telugu voice responses using Gnani Timbre.
- Scheme details, required documents, application information and source links.
- Follow-up questions to collect missing eligibility information.

## Technology Stack
- Python
- Streamlit
- Gnani Prisma (Speech-to-Text)
- Gnani Timbre (Text-to-Speech)
- Google Gemini
- JSON

## How It Works
1. User asks a question through voice.
2. Gnani Prisma converts speech into text.
3. Google Gemini interprets the user's query.
4. A rule-based engine checks the available scheme eligibility criteria.
5. Gnani Timbre generates a spoken response in Telugu.

## Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd aasara
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure your API credentials using Streamlit secrets.

Run the application:

```bash
streamlit run app.py
```

## Gnani AI Integration
- Prisma v2.5 – Speech-to-Text
- Timbre v2.5 – Text-to-Speech

## Limitations
- Currently covers 9 schemes.
- Telangana scheme details based on news reports are marked for local confirmation.
- Provides informational eligibility estimates, not official government decisions.
- Speech accuracy has not yet been formally measured.

## Project Links
- Demo Video: (https://lnkd.in/p/di8q_QQ7)
- Solution Pitch: Solution-Pitch.pdf

## Disclaimer
Aasara is an independent informational project and is not an official government service.