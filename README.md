# SCIENCEMENTOR 🧬

AI-powered Biology tutor for Malaysian Form 4 secondary school students.

## Quick Start

### 1. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
# Edit .env and add your API keys
```

Configure at least one provider:

- `OPENAI_API_KEY` - For OpenAI GPT
- `ANTHROPIC_API_KEY` - For Claude
- `GOOGLE_API_KEY` - For Gemini
- `OLLAMA_BASE_URL` - For local Ollama (default: http://localhost:11434)

### 3. Run Backend

```bash
python app.py
```

Backend runs at: http://localhost:5000

### 4. Open Frontend

Open `frontend/index.html` in your browser, or serve it:

```bash
cd frontend
python -m http.server 8000
```

Frontend at: http://localhost:8000

## API Endpoints

| Endpoint     | Method | Description                  |
| ------------ | ------ | ---------------------------- |
| `/health`    | GET    | Health check                 |
| `/providers` | GET    | List available LLM providers |
| `/topics`    | GET    | List Biology topics          |
| `/ask`       | POST   | Ask a Biology question       |

### Example Request

```bash
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is mitosis?", "provider": "openai"}'
```

## Supported LLM Providers

- **OpenAI** - GPT-3.5 Turbo
- **Claude** - Claude 3 Haiku
- **Gemini** - Gemini 1.5 Flash
- **Ollama** - Local models (llama3, mistral)

## Biology Topics Covered

1. Cell Structure & Organelles
2. Cell Division (Mitosis/Meiosis)
3. Enzymes
4. Photosynthesis
5. Respiration
6. Diffusion & Osmosis
7. Digestive System
8. Circulatory System
9. DNA & Genes

## Deployment

### Render

1. Connect your GitHub repo to Render
2. Add your API keys as environment variables
3. Deploy using the `render.yaml` blueprint

### Docker

```bash
docker build -t sciencementor .
docker run -p 5000:5000 --env-file backend/.env sciencementor
```
