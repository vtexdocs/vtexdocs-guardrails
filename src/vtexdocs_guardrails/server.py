"""Flask HTTP server for guardrails validation."""

import os
import logging
import time
from typing import Optional
from flask import Flask, request, jsonify
from .validator import JailbreakValidator
from .config import Config

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def create_app(config: Optional[Config] = None) -> Flask:
    """
    Create and configure Flask application.
    
    Args:
        config: Configuration object (defaults to environment-based config)
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    if config is None:
        config = Config.from_env()
    
    # Initialize validator
    logger.info("Initializing jailbreak validator...")
    validator = JailbreakValidator(
        threshold=config.jailbreak_threshold,
        device=config.jailbreak_device,
    )
    logger.info("Validator initialized successfully")
    
    # Metrics
    metrics = {
        "total_requests": 0,
        "blocked_requests": 0,
        "total_latency_ms": 0.0,
    }
    
    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "model_loaded": validator.is_loaded,
            "validator": "detect_jailbreak",
            "device": config.jailbreak_device,
            "threshold": config.jailbreak_threshold,
        }), 200
    
    @app.route("/validate", methods=["POST"])
    def validate():
        """Validate text for jailbreak attempts."""
        start_time = time.perf_counter()
        
        # Parse request
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({
                "error": "Missing required field 'text'",
                "is_safe": False,
            }), 400
        
        text = data["text"]
        threshold_override = data.get("threshold")
        
        # Override threshold if provided
        if threshold_override is not None:
            try:
                threshold_override = float(threshold_override)
                if not 0.0 <= threshold_override <= 1.0:
                    raise ValueError("Threshold must be between 0.0 and 1.0")
            except (ValueError, TypeError) as e:
                return jsonify({
                    "error": f"Invalid threshold: {e}",
                    "is_safe": False,
                }), 400
        
        # Validate
        is_safe, score, reason = validator.validate(text)
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        # Update metrics
        metrics["total_requests"] += 1
        metrics["total_latency_ms"] += latency_ms
        if not is_safe:
            metrics["blocked_requests"] += 1
        
        # Build response
        response = {
            "is_safe": is_safe,
            "score": round(score, 4),
            "threshold": threshold_override or validator.threshold,
            "latency_ms": round(latency_ms, 2),
            "model": "jackhhao/jailbreak-classifier",
        }
        
        if not is_safe:
            response["reason"] = reason or "Potential jailbreak detected"
            return jsonify(response), 400
        
        return jsonify(response), 200
    
    @app.route("/metrics", methods=["GET"])
    def get_metrics():
        """Get service metrics."""
        avg_latency = (
            metrics["total_latency_ms"] / metrics["total_requests"]
            if metrics["total_requests"] > 0
            else 0.0
        )
        
        return jsonify({
            "total_requests": metrics["total_requests"],
            "blocked_requests": metrics["blocked_requests"],
            "block_rate": (
                metrics["blocked_requests"] / metrics["total_requests"]
                if metrics["total_requests"] > 0
                else 0.0
            ),
            "avg_latency_ms": round(avg_latency, 2),
        }), 200
    
    return app


def main():
    """CLI entry point."""
    config = Config.from_env()
    app = create_app(config)
    
    logger.info(f"Starting server on {config.host}:{config.port}")
    app.run(
        host=config.host,
        port=config.port,
        debug=config.debug,
    )


if __name__ == "__main__":
    main()
