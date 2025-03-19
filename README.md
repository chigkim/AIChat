Generate a conversation between two models using OpenAI API and Kokoro TTS.

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

