# WaterBuddy 💧

**A personalized hydration companion built with Python and Streamlit.**

WaterBuddy works by bringing a user’s hydration activity into one personalized workflow: users register or sign in, set up their profile, and log water intake through the tracking interface; the app stores relevant profile and hydration records in SQLite, updates progress against the user’s daily goal, and uses its hydration and goal-optimization services to calculate progress and support personalization. Dashboard and analytics pages turn recorded intake into visual summaries with Plotly, while achievements, daily tasks, and reminders help users maintain consistent habits. For additional support, the AI coach and bottle-image scanning features send supported prompts or images to the configured AI service through the OpenAI-compatible client and OpenRouter; weather-aware features retrieve conditions from OpenWeatherMap, and voice features use SpeechRecognition for speech input and gTTS for spoken output. Streamlit powers the interactive application, reusable components organize the interface, and custom CSS provides its visual styling; features that rely on external services require internet access and correctly configured API credentials.

> **Project status:** Personal/educational project. AI, voice, and weather functionality depend on external services and valid configuration. WaterBuddy is a wellness aid, not a medical device or a substitute for professional medical advice.

## Contents

- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Application Architecture](#application-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Privacy, Security, and Limitations](#privacy-security-and-limitations)
- [Credits and Acknowledgements](#credits-and-acknowledgements)
- [Deployment Notes](#deployment-notes)

## Overview

WaterBuddy brings hydration tracking and habit-building tools together in one application. Users can create an account, complete a personal profile, record water intake, review progress, and explore supporting features such as an AI coach, voice assistant, achievements, and weather-aware hydration context.

The application is organized into separate pages, reusable interface components, service modules, and database utilities to keep the interface and application logic maintainable.

## Features

### Hydration tracking and goals
- **Daily intake logging:** Record water consumption and maintain a running daily total.
- **Quick-add tracking:** Add common amounts of water with fewer interactions.
- **Daily goal management:** Set and review a hydration target.
- **Goal optimization:** Use the application's goal logic and available profile/context information to help personalize targets.
- **Progress feedback:** See current intake in relation to the daily goal.
- **Persistent records:** Store user profiles and hydration data locally using SQLite.

### Personalization and account management
- **Account registration and login:** Create an account and sign in.
- **Profile setup:** Save profile information used by personalization features.
- **Personalized experience:** Adapt parts of the application to saved profile and activity context.
- **Session and navigation management:** Keep the app's pages and user state organized.
- **Settings and themes:** Access preferences and supported visual themes.

### Insights and motivation
- **Interactive analytics:** Explore hydration data through Plotly visualizations.
- **Statistics and progress summaries:** Review intake information over time where data is available.
- **Achievements and milestones:** Encourage consistency through progress-based recognition.
- **Daily tasks and reminders:** Use built-in task/reminder features to support a regular hydration routine.
- **Hydration visuals and mascot:** Present progress through reusable visual components and friendly interface elements.

### AI-assisted tools
- **AI hydration coaching:** Ask for hydration-related guidance and contextual suggestions.
- **Context-aware responses:** Use available profile and application context to make AI interactions more relevant.
- **Bottle/image scanning:** Submit an image for AI-assisted analysis where the configured model and service support it.
- **Hydration-twin/context features:** Use the application's context and goal-support logic to provide a more personalized experience.

AI-generated responses and image analysis may be inaccurate. Treat them as general informational support rather than medical recommendations.

### Voice and environmental context
- **Voice assistant:** Access voice-oriented interaction through the application's voice page.
- **Speech-to-text:** Use the SpeechRecognition package with its configured Google recognition service to transcribe supported speech input.
- **Text-to-speech:** Use gTTS to generate spoken output for supported features.
- **Weather-aware context:** Retrieve weather information through the OpenWeatherMap service when configured.
- **Fallback handling:** Some integrations may be unavailable or limited when API credentials, internet access, or third-party services are unavailable.

### Interface and engineering
- **Streamlit application shell:** Run the app as a Python web application.
- **Custom styling:** Use project CSS for a glassmorphism-inspired visual design.
- **Reusable UI components:** Share cards, reminders, hydration visuals, and mascot elements across pages.
- **Modular architecture:** Separate page rendering, hydration logic, AI integrations, weather, speech, and data management.
- **Local database:** Use SQLite for local application records.
- **Configuration through environment variables:** Keep API credentials out of the source code by loading local configuration with python-dotenv.
- **Testing support:** The repository includes test files and helper scripts for checking application behavior.

## How It Works

WaterBuddy is written in Python and uses Streamlit for its application interface and navigation. The pages in `pages/` provide the main user-facing tools, while `components/` contains reusable interface elements and `services/` holds hydration, analytics, personalization, AI, weather, and speech-related logic. SQLite stores application data locally, and Plotly renders interactive charts. Custom CSS defines the visual theme. The OpenAI Python SDK is used as an OpenAI-compatible client for the configured OpenRouter model service; OpenWeatherMap supplies weather data, SpeechRecognition provides speech transcription integration, and gTTS provides text-to-speech. API-dependent features require suitable credentials and network access.

## Application Architecture

WaterBuddy follows a modular, page-and-service architecture. Streamlit provides the presentation layer, page modules coordinate user interactions, service modules contain feature logic, and the database layer handles persistent records.

```text
User
  │
  ▼
Streamlit UI (app.py and pages/)
  │
  ├── Reusable interface (components/ and styles/)
  │
  ▼
Core navigation, configuration, and session management (core/)
  │
  ▼
Feature services (services/)
  ├── Hydration, goals, personalization, and analytics
  ├── AI coaching and image-based analysis ──► OpenRouter / configured model
  ├── Weather context ───────────────────────► OpenWeatherMap
  └── Speech input and spoken output ─────────► SpeechRecognition / gTTS
  │
  ▼
Data access and local persistence (database/)
  │
  ▼
SQLite database
```

- **Presentation layer:** `app.py`, `pages/`, `components/`, and `styles/` provide navigation, screens, reusable UI, and visual design.
- **Application/core layer:** `core/` organizes configuration, navigation, themes, and session-related behavior.
- **Service layer:** `services/` separates hydration calculations, goal support, analytics, personalization, and external integrations from page layout.
- **Data layer:** `database/` manages SQLite-backed application records.
- **Integration layer:** AI, weather, speech recognition, and text-to-speech features use external services or libraries when configured.

This diagram describes the intended module responsibilities at a high level; exact call paths and data handling depend on the current implementation in the repository.

## Technology Stack

| Technology / service | Role in WaterBuddy |
| --- | --- |
| [Python](https://www.python.org/) | Core programming language |
| [Streamlit](https://streamlit.io/) | Web application interface, widgets, and navigation |
| [SQLite](https://www.sqlite.org/) | Local relational data storage |
| [Plotly](https://plotly.com/python/) | Interactive data visualization |
| [OpenAI Python SDK](https://github.com/openai/openai-python) | API client used with an OpenAI-compatible endpoint |
| [OpenRouter](https://openrouter.ai/) | Model API routing for supported AI features |
| [OpenWeatherMap](https://openweathermap.org/api) | Weather data integration |
| [SpeechRecognition](https://github.com/Uberi/speech_recognition) | Speech recognition integration |
| [Google speech recognition service](https://www.google.com/) | Recognition backend used by the configured SpeechRecognition integration |
| [gTTS](https://gtts.readthedocs.io/) | Text-to-speech generation |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | Loading environment variables from a local `.env` file |
| HTML and CSS | Custom interface styling and visual effects |

## Project Structure

```text
WaterBuddy/
├── app.py                 # Application entry point and authentication flow
├── pages/                 # Dashboard, tracking, goals, profile, AI, voice, and more
├── components/            # Reusable UI elements and hydration visuals
├── services/              # Hydration logic, analytics, AI, weather, and speech services
├── database/              # SQLite database management and data access
├── core/                  # Navigation, session management, configuration, and themes
├── styles/                # Custom styling
├── assets/                # Application assets
├── tests/                 # Test suite and testing utilities
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment configuration
└── Procfile               # Deployment process configuration
```

## Getting Started

### Prerequisites

- Python 3.10 or a compatible version supported by the installed dependencies.
- pip.
- Internet access for features that call external services.
- API credentials for any external integrations you want to enable.

### Run locally

1. Clone the repository and enter the project directory:

   ```bash
   git clone https://github.com/adrian-hue-pixel/WaterBuddy.git
   cd WaterBuddy
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   macOS/Linux:

   ```bash
   source .venv/bin/activate
   ```

   Windows PowerShell:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a local `.env` file and add the API keys required for your chosen features. See [Configuration](#configuration).

5. Start the application:

   ```bash
   streamlit run app.py
   ```

6. Open the local URL printed in your terminal by Streamlit.

## Configuration

Store credentials in a local `.env` file. **Never commit real API keys, tokens, or passwords to GitHub.**

Common configuration variables used by the integrations include:

| Variable | Purpose |
| --- | --- |
| `OPENROUTER_API_KEY` | Authentication for AI features that use the OpenRouter endpoint |
| `OPENWEATHER_API_KEY` | Authentication for weather data from OpenWeatherMap |

Configuration names can vary between versions of the code. Check the relevant service module before deploying, and ensure the local `.env.example` matches the variables expected by the current source code. Features that do not require external APIs may still work without these keys.

## Privacy, Security, and Limitations

### Data and privacy
- **Local storage:** SQLite is used for application records. The exact data stored depends on the enabled features and current implementation.
- **Third-party processing:** AI prompts and bottle images, speech sent for recognition, and weather queries may be transmitted to external providers when those features are used. Review each provider's privacy policy and terms before use.
- **Data minimization:** Avoid entering passwords, financial information, precise personal details, or other sensitive information into AI prompts or image-scanning features.
- **Deployment matters:** Local development and public hosting have different privacy implications. A hosted app may make data accessible to the hosting operator or deployment environment.
- **Retention and deletion:** Check the database and service code to understand what is saved, how long it remains, and how a user can remove it. Do not assume data is automatically deleted.

### Security considerations
- **Secrets management:** Keep API keys and credentials in local environment variables or the hosting platform's secrets manager. Never commit real secrets to Git, include them in screenshots, or expose them in client-visible output.
- **Authentication review:** Before real users rely on the app, verify password hashing, login validation, session handling, access controls, and protections against unauthorized account or database access in the actual source code.
- **Database protection:** SQLite is local storage, not a complete production security system. Protect the database file and host filesystem, restrict access, and establish appropriate backup and deletion procedures.
- **External API boundaries:** Send only the data needed for each request. Use HTTPS endpoints, check API error handling, and avoid logging tokens, passwords, prompts, or other sensitive content unnecessarily.
- **Production readiness:** Before public deployment, review dependency updates, input validation, exception handling, rate limits, authorization, secure configuration, and the hosting platform's filesystem persistence.
- **No security certification claim:** These notes describe recommended safeguards, not a guarantee that the current app has passed a security audit or penetration test. Verify each control in the implementation before describing it as implemented.

### Functional and health limitations
- AI-generated responses and image analysis can be inaccurate, and weather results depend on the provider.
- Speech and AI features require compatible configuration, internet access, and third-party availability.
- Hydration needs vary by individual and circumstance. WaterBuddy's targets and AI responses are informational only and are not medical advice.

## Testing

WaterBuddy was reviewed with feedback from friends, family members, and teachers. Based on their suggestions, I made improvements and adjustments to the app to make the experience clearer, more useful, and more user-friendly.

## Credits and Acknowledgements

**Name of student:** Adrian Rohith C  
**Reg. No.:** 1000528  
**Mentor:** Syed Ali Beema S  
**Name of the school:** Jain Vidyalaya

WaterBuddy is an independent educational project assembled using the open-source libraries and external services listed below. Each project and provider retains ownership of its own software, trademarks, documentation, and services. Please consult each linked project for its current license, usage terms, and attribution requirements.

- **Python** — programming language: [python.org](https://www.python.org/)
- **Streamlit** — application framework: [streamlit.io](https://streamlit.io/)
- **SQLite** — embedded database engine: [sqlite.org](https://www.sqlite.org/)
- **Plotly** — interactive charts and visualization: [plotly.com](https://plotly.com/python/)
- **OpenAI Python SDK** — API client library: [GitHub repository](https://github.com/openai/openai-python)
- **OpenRouter** — access to compatible AI model APIs: [openrouter.ai](https://openrouter.ai/)
- **OpenWeatherMap** — weather API provider: [openweathermap.org](https://openweathermap.org/api)
- **SpeechRecognition** — Python speech-recognition library: [GitHub repository](https://github.com/Uberi/speech_recognition)
- **gTTS** — Google Text-to-Speech Python library: [documentation](https://gtts.readthedocs.io/)
- **python-dotenv** — environment-variable loading utility: [GitHub repository](https://github.com/theskumar/python-dotenv)

### Third-party assets

The interface includes project styling and visual components. Any third-party images, icons, fonts, illustrations, or sound assets should be credited here with the original creator, source URL, and license. No external asset creator is attributed in this document unless the asset and its source have been verified.

### Project attribution

Created and maintained in the [WaterBuddy GitHub repository](https://github.com/adrian-hue-pixel/WaterBuddy). Contributions, suggestions, and bug reports can be submitted through GitHub.

## Deployment Notes

- **Streamlit Community Cloud:** Connect the repository and configure the app entry point as `app.py`; add required secrets in the deployment settings.
- **Heroku-compatible deployment:** The repository includes a `Procfile`; confirm that the target platform and dependencies are current before deployment.
- **Database persistence:** The local SQLite database is suitable for local development. Verify persistent disk and database requirements before using a hosting platform where the filesystem may be ephemeral.
- **External integrations:** Configure required API keys in the hosting provider's secret/environment settings rather than committing them to the repository.

---

*WaterBuddy is a software project for hydration habit support and educational use. Use it thoughtfully, verify AI-generated information, and consult qualified professionals for individual health concerns.*
