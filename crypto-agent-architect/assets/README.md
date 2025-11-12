# Crypto Agent Template Assets

This directory contains boilerplate templates for crypto trading agents.

## crypto-agent-template/

FastAPI-based crypto trading agent project template with 5-layer architecture pre-configured.

**Use the init script instead:**

```bash
python scripts/init_crypto_agent.py \
  --name my-trading-bot \
  --exchange binance \
  --strategies momentum,mean-reversion \
  --llm-providers openai,anthropic \
  --output ./my-trading-bot
```

The init script generates a complete project structure with:

- **src/consensus/** - Layer 1: Smart Consensus (Multi-LLM decision making)
- **src/adapters/** - Layer 2: Exchange Adapters (Binance, Coinbase, etc.)
- **src/strategies/** - Layer 3: Trading Strategy (Risk management, position sizing)
- **src/data/** - Layer 4: Data Pipeline (Market data ingestion, validation, caching)
- **src/monitoring/** - Layer 5: Monitoring & Observability (Prometheus, Grafana, alerts)
- **tests/** - Unit, integration, and E2E tests
- **config/** - Risk rules, exchange settings, monitoring configuration
- **docker-compose.yml** - Infrastructure (Redis, Postgres, Prometheus, Grafana)
- **pyproject.toml** - Python dependencies and project configuration

## Template Features

- **Production-ready:** Circuit breakers, rate limiting, retry logic
- **High test coverage:** 80%+ test coverage target with pytest
- **Real-time monitoring:** Prometheus metrics, Grafana dashboards
- **Risk management:** Position sizing, drawdown limits, kill switch
- **Multi-LLM consensus:** Aggregate decisions from multiple models
- **Resilient APIs:** Automatic retries, circuit breakers, rate limiting

## Customization

After generating a project:

1. **Configure API keys:** Edit `.env` with your API credentials
2. **Adjust risk rules:** Modify `config/risk_rules.yaml` for your risk tolerance
3. **Select exchanges:** Configure `config/exchanges.yaml` with target exchanges
4. **Implement strategies:** Add trading strategies in `src/strategies/`
5. **Configure monitoring:** Set up alerts in `config/monitoring.yaml`

## Getting Started

```bash
# Generate project
python scripts/init_crypto_agent.py --name my-bot --exchange binance --strategies momentum --llm-providers openai --output ./my-bot

# Install dependencies
cd my-bot
poetry install

# Start infrastructure
docker-compose up -d

# Run tests
pytest --cov=src

# Start agent (paper trading)
python -m src.main --mode paper
```

## Architecture Validation

Validate your project follows the 5-layer architecture:

```bash
python scripts/validate_architecture.py ./my-bot
```

This checks:
- All 5 layers are present and properly structured
- Dependencies between layers are correct
- Test coverage meets 80% target
- Configuration files are present
- Integration between layers is working
