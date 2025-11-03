FROM python:3.11-slim

# Build arg for Guardrails Hub token (required for installing validators)
# Get a free token at: https://hub.guardrailsai.com/tokens
ARG GUARDRAILS_TOKEN

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./
COPY src/ ./src/

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install PyTorch CPU-only first to avoid CUDA bloat (~10GB saved)
RUN uv pip install --system --no-cache \
    torch --index-url https://download.pytorch.org/whl/cpu

# Install package dependencies
RUN uv pip install --system --no-cache -e .

# Configure guardrails with local models (no runtime dependencies on Guardrails Hub)
RUN guardrails configure --enable-metrics --disable-remote-inferencing --token "${GUARDRAILS_TOKEN}" && \
    guardrails hub install hub://guardrails/detect_jailbreak --install-local-models

RUN useradd --create-home --shell /bin/bash --uid 1000 guardrails && \
    chown -R guardrails:guardrails /app
USER guardrails

EXPOSE 8082

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8082/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8082", "--workers", "2", "--timeout", "90", \
    "--access-logfile", "-", "--error-logfile", "-", \
    "--worker-class", "sync", "vtexdocs_guardrails.server:create_app()"]
