# AIChat

Generate conversations between two LLMs on any topic using the OpenAI API. You can mix and match models from Ollama, MLX, Claude, OpenAI, Google AI Studio, etc. that uses OpenAI API. It uses Kokoro-ONNX for TTS.

Conversation Demo: https://www.youtube.com/watch?v=FgSZLZnYlAE

## Usage

1. Specify base_url, api_key, model, etc. in config.toml.
2. Customize the topic and system prompt for each nmodel in chat.py.

```bash
python3 -m venv .venv
# Linux/mac
source .venv/bin/activate
# Windows: .venv\scripts\activate
pip install -r requirements.txt
python chat.py
```

