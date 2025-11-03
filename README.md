# VTEX Docs Guardrails

Jailbreak detection service for VTEX Docs AI agents using Guardrails AI Hub.

## Features

- **Jailbreak Detection**: Uses `jackhhao/jailbreak-classifier` model (BERT-based)
- **HTTP API**: Flask-based REST API with `/validate` and `/health` endpoints
- **CPU Optimized**: Runs efficiently on CPU without GPU requirements
- **Docker Ready**: Includes Dockerfile and docker-compose for easy deployment
- **Configurable**: Threshold and device selection via environment variables
- **Metrics**: Built-in `/metrics` endpoint for monitoring

## Quick Start

### Prerequisites

**Guardrails Hub Token (One-time setup)**

You need a free token from Guardrails Hub to download validators during the build:

1. Sign up for a free account at https://hub.guardrailsai.com/
2. Get your token at https://hub.guardrailsai.com/tokens
3. The token is only needed during build/installation - no runtime dependencies

### Local Development

```bash
# Install dependencies
pip install -e ".[test]"

# Configure guardrails with your token
guardrails configure --token "YOUR_TOKEN_HERE"
guardrails hub install hub://guardrails/detect_jailbreak --install-local-models

# Run server
python -m vtexdocs_guardrails.server
```

Server will be available at `http://localhost:8082`

### Docker

```bash
# Build with your Guardrails Hub token
docker build --build-arg GUARDRAILS_TOKEN="YOUR_TOKEN_HERE" -t vtexdocs-guardrails .

# Run
docker run -p 8082:8082 vtexdocs-guardrails
```

**Note**: The token is only used during the Docker build to download the jailbreak detection model. Once built, the image runs completely offline with no external dependencies.

## API Reference

### POST /validate

Validate text for jailbreak attempts.

**Request:**
```json
{
  "text": "string (required)",
  "threshold": 0.5 (optional, default from config)
}
```

**Response (200 OK - Safe):**
```json
{
  "is_safe": true,
  "score": 0.23,
  "threshold": 0.5,
  "latency_ms": 145,
  "model": "jackhhao/jailbreak-classifier"
}
```

**Response (400 Bad Request - Blocked):**
```json
{
  "is_safe": false,
  "score": 0.87,
  "threshold": 0.5,
  "reason": "Potential jailbreak detected",
  "latency_ms": 152,
  "model": "jackhhao/jailbreak-classifier"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "validator": "detect_jailbreak",
  "device": "cpu",
  "threshold": 0.5
}
```

### GET /metrics

Service metrics.

**Response:**
```json
{
  "total_requests": 1234,
  "blocked_requests": 45,
  "block_rate": 0.0365,
  "avg_latency_ms": 167.3
}
```

## Configuration

Environment variables:

- `GUARDRAILS_HOST`: Server host (default: 0.0.0.0)
- `GUARDRAILS_PORT`: Server port (default: 8082)
- `JAILBREAK_THRESHOLD`: Detection threshold 0.0-1.0 (default: 0.5)
- `JAILBREAK_DEVICE`: Device to use: cpu, cuda, metal (default: cpu)
- `LOG_LEVEL`: Logging level (default: INFO)
- `ENVIRONMENT`: production or development (default: production)

## Testing

```bash
pytest tests/
pytest tests/ -v  # Verbose
pytest tests/ --cov=src/vtexdocs_guardrails  # With coverage
```

## Model Information

- **Model**: `jackhhao/jailbreak-classifier`
- **Type**: BERT-based text classification
- **Size**: ~110MB
- **Input**: Text prompts
- **Output**: Jailbreak probability score (0.0-1.0)
- **Training Data**: Jailbreak attempts and legitimate prompts
- **Monthly Downloads**: ~3,891 (from Hugging Face)

## Performance

- **Latency**: 100-300ms per request (CPU)
- **Throughput**: ~10-20 req/s per worker
- **Memory**: ~200MB (model) + ~300MB (runtime)
- **Startup Time**: 30-60s (model loading)

## Architecture

The service uses Guardrails AI Hub's `DetectJailbreak` validator, which wraps the BERT-based jailbreak classifier from jackhhao. The validator runs locally without requiring external API calls.

## Development

### Adding New Validators

To add additional validators (e.g., PII detection, toxic language):

```python
from .validator import JailbreakValidator
from guardrails.hub import DetectPII

class EnhancedValidator:
    def __init__(self):
        self.jailbreak = JailbreakValidator()
        # Add more validators as needed
```

### Troubleshooting

**Model not loading:**
```bash
# Re-configure guardrails
guardrails configure --token ""
guardrails hub install hub://guardrails/detect_jailbreak
```

**Port already in use:**
```bash
# Use different port
GUARDRAILS_PORT=8083 python -m vtexdocs_guardrails.server
```

**High false positive rate:**
- Decrease `JAILBREAK_THRESHOLD` (more lenient)
- Example: `JAILBREAK_THRESHOLD=0.3`

## License

MIT

## Contributing

Issues and pull requests are welcome. Please follow the existing code style and add tests for new features.
