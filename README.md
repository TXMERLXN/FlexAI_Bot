# ComfyUI Telegram Bot

A complex automation system that integrates ComfyUI with Telegram, using multiple Kaggle accounts for continuous operation.

## Features

- Telegram bot interface for ComfyUI image generation
- Multiple workflow support with JSON-based configuration
- Automatic Kaggle account management for 24/7 operation
- GitHub integration for code and file management
- Comprehensive logging and monitoring

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with the following variables:
```env
TELEGRAM_TOKEN=your_telegram_token
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
KAGGLE_NOTEBOOK_URL=your_notebook_url
GITHUB_TOKEN=your_github_token
GITHUB_REPO=your_github_repo
```

3. Add ComfyUI workflows to the `workflows` directory in JSON format.

## Usage

1. Start the bot:
```bash
python bot.py
```

2. In Telegram:
   - Use `/start` to begin
   - Select a workflow from the available options
   - Send a text prompt or image to generate new images

## Directory Structure

```
├── bot.py                 # Main Telegram bot code
├── comfyui_manager.py     # ComfyUI integration
├── kaggle_manager.py      # Kaggle account management
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── workflows/           # ComfyUI workflow JSON files
└── logs/               # Application logs
```

## Kaggle Account Management

The system automatically manages multiple Kaggle accounts to ensure 24/7 operation:
- Switches accounts every 12.5 hours
- Tracks usage and maintains account rotation
- Handles authentication and API key management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License
