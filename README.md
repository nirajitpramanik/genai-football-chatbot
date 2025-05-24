# Football GenAI Chatbot

A comprehensive GenAI chatbot built with Python and Streamlit that can answer questions about football players, teams, transfers, and statistics using the Transfermarkt API.

## Features

- 🏆 Player information and statistics
- 🏟️ Team details and squad information
- 🔄 Transfer history and market values
- 📊 League tables and standings
- 🤖 AI-powered natural language responses
- 💬 Context-aware conversations
- 🎨 Multiple response styles (Casual, Professional, Detailed)

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- WSL Linux environment (if on Windows)
- Gemini API key

### Installation

1. Clone or create the project directory:
```bash
mkdir football-chatbot
cd football-chatbot
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On WSL/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env file with your Gemini API key (optional)
```

### Running the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Usage Examples

- "Tell me about Lionel Messi"
- "Real Madrid team info"
- "Cristiano Ronaldo transfers"
- "Premier League table"
- "Compare Messi and Ronaldo"

## Architecture

The chatbot consists of several key components:

1. **Data Fetcher** - Integrates with Transfermarkt API
2. **Intent Processor** - Analyzes user questions and extracts entities
3. **Response Generator** - Creates natural language responses using AI or templates
4. **Streamlit Interface** - Provides the web-based chat interface

## API Integration

This chatbot uses the Transfermarkt API (https://transfermarkt-api.fly.dev) for football data. The API provides:

- Player search and detailed information
- Team/club information and squads
- Transfer histories and market values
- Competition data and standings

## Deployment Options

### Local Development
```bash
streamlit run app.py
```

## Configuration

- **Response Style**: Choose between Casual, Professional, or Detailed
- **AI Enhancement**: Use Gemini API for more natural responses
- **Caching**: Built-in caching for API responses
- **Logging**: Comprehensive logging for debugging

## Learning Objectives

This project teaches:
- GenAI chatbot development
- API integration and data handling
- Natural language processing
- Intent recognition and entity extraction
- Context management in conversations
- Web application development with Streamlit
- Deployment strategies

## Troubleshooting

### Common Issues

1. **API Rate Limiting**: The app includes built-in rate limiting and retry logic
2. **Memory Constraints**: Uses lightweight models and template responses as fallback
3. **Data Quality**: Implements data validation and error handling

### Support

For issues and questions, check the logs in the `logs/` directory for detailed error information.

## Contributing

Feel free to extend the chatbot with additional features:
- More sophisticated AI models
- Additional data sources
- Voice interface
- Multi-language support
- Advanced analytics

## License

This project is for educational purposes. Please respect the terms of service of the APIs used.
