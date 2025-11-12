---
name: crypto-agent-architect
description: Design production-grade crypto trading agents with 5-layer architecture (Smart Consensus, Binance Adapter, Trading Strategy, Data Pipeline, Monitoring). Use for crypto trading bots, DeFi agents, exchange integrations with Binance/dYdX. Implements multi-LLM consensus, resilient API patterns, risk management, and 80%+ test coverage.
---

# Crypto Agent Architect

## Overview

Design and implement production-grade cryptocurrency trading agents using a battle-tested 5-layer architecture. This skill provides comprehensive guidance for building robust crypto trading systems with multi-LLM consensus decision-making, resilient exchange integrations, advanced risk management, real-time data pipelines, and enterprise-grade observability.

**Use this skill when:**
- Building automated crypto trading bots for CEX (Binance, Coinbase, Kraken) or DEX (Uniswap, dYdX)
- Creating DeFi agents for yield farming, arbitrage, or liquidity provision
- Implementing multi-strategy trading systems with AI-powered decision-making
- Integrating crypto trading capabilities into existing applications
- Requiring production-grade resilience, monitoring, and risk controls
- Needing 80%+ test coverage for financial systems

## Core Architecture

The 5-layer architecture provides separation of concerns and production-grade reliability:

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: Smart Consensus (Multi-LLM Decision Making)   │
├─────────────────────────────────────────────────────────┤
│  Layer 2: Binance Adapter (Resilient Exchange API)      │
├─────────────────────────────────────────────────────────┤
│  Layer 3: Trading Strategy (Risk & Position Management) │
├─────────────────────────────────────────────────────────┤
│  Layer 4: Data Pipeline (Market Data & Validation)      │
├─────────────────────────────────────────────────────────┤
│  Layer 5: Monitoring & Observability (Metrics & Alerts) │
└─────────────────────────────────────────────────────────┘
```

## 1. Smart Consensus Layer

**Responsibility:** Aggregate multiple LLM opinions to make high-confidence trading decisions through voting consensus, reducing single-model hallucination risk.

**Uses:** `consensus-engine` skill (Tier 2)

### Key Components

**Consensus Manager** - Orchestrates multi-LLM voting:

```python
from consensus_engine import ConsensusEngine, VotingStrategy

class TradingConsensusManager:
    """Manage multi-LLM consensus for trading decisions"""

    def __init__(self, models: list[str], strategy: VotingStrategy):
        self.engine = ConsensusEngine(
            models=models,  # ["gpt-4", "claude-3-opus", "gemini-pro"]
            strategy=strategy,  # MAJORITY, UNANIMOUS, WEIGHTED
            confidence_threshold=0.75
        )

    async def decide_trade(
        self,
        market_data: dict,
        portfolio: dict
    ) -> TradeDecision:
        """Get consensus on whether to trade"""

        prompt = f"""
        Market: {market_data['symbol']}
        Price: ${market_data['price']}
        24h Change: {market_data['change_24h']}%
        Volume: ${market_data['volume_24h']:,.0f}
        RSI: {market_data['indicators']['rsi']}
        MACD: {market_data['indicators']['macd']}

        Portfolio: ${portfolio['total_value']:,.2f}
        Available: ${portfolio['available_balance']:,.2f}
        Positions: {portfolio['open_positions']}

        Should we BUY, SELL, or HOLD? Provide reasoning.
        """

        result = await self.engine.get_consensus(
            prompt=prompt,
            response_format={
                "decision": "BUY|SELL|HOLD",
                "confidence": "float",
                "reasoning": "string"
            }
        )

        return TradeDecision(
            action=result.consensus_value["decision"],
            confidence=result.confidence_score,
            reasoning=result.consensus_value["reasoning"],
            votes=result.votes,
            timestamp=result.timestamp
        )
```

**Decision Validator** - Validate consensus meets risk criteria:

```python
class DecisionValidator:
    """Validate trading decisions against risk rules"""

    def validate(
        self,
        decision: TradeDecision,
        rules: RiskRules
    ) -> ValidationResult:
        """Validate decision meets all criteria"""

        checks = [
            self._check_confidence_threshold(decision, rules),
            self._check_position_sizing(decision, rules),
            self._check_drawdown_limits(decision, rules),
            self._check_volatility_constraints(decision, rules),
            self._check_correlation_limits(decision, rules)
        ]

        passed = all(check.passed for check in checks)

        return ValidationResult(
            passed=passed,
            checks=checks,
            approved_decision=decision if passed else None,
            rejection_reason=self._get_failure_reasons(checks)
        )
```

### Crypto-Specific Considerations

- **Gas Fee Awareness:** For DEX trades, consensus must account for gas costs that can exceed profit on small trades
- **Slippage Protection:** High slippage (>2%) should override LLM buy recommendations
- **Flash Crash Detection:** Implement circuit breakers when consensus detects >20% price drops in <5 minutes
- **MEV Protection:** For DeFi, consider flashbots/private mempools to prevent front-running

### Design Patterns

- **Strategy Pattern:** Different consensus strategies (majority, unanimous, weighted by model performance)
- **Chain of Responsibility:** Validation pipeline with multiple risk checks
- **Observer Pattern:** Notify monitoring system of all consensus decisions

### Test Coverage Requirements

- **Unit Tests (95%):** Test each consensus strategy, validator check independently
- **Integration Tests (85%):** Test full consensus → validation → decision flow
- **Chaos Tests:** Simulate LLM API failures, timeouts, conflicting responses

**Test Example:**

```python
@pytest.mark.asyncio
async def test_consensus_rejects_high_risk_during_volatility():
    """Consensus should reject risky trades during high volatility"""

    manager = TradingConsensusManager(
        models=["gpt-4", "claude-3-opus"],
        strategy=VotingStrategy.MAJORITY
    )

    # Simulate high volatility market
    market_data = {
        "symbol": "BTC/USDT",
        "price": 45000,
        "change_24h": -15.5,  # High volatility
        "volume_24h": 2_000_000_000,
        "indicators": {"rsi": 35, "macd": -500}
    }

    portfolio = {
        "total_value": 100000,
        "available_balance": 50000,
        "open_positions": 2
    }

    decision = await manager.decide_trade(market_data, portfolio)

    # Validator should reject due to high volatility
    validator = DecisionValidator()
    result = validator.validate(decision, RiskRules(max_volatility=10))

    assert result.passed is False
    assert "volatility" in result.rejection_reason.lower()
```

## 2. Binance Adapter Layer

**Responsibility:** Provide resilient, rate-limited interface to Binance API with automatic retries, circuit breakers, and error recovery.

**Uses:** `resilience-patterns` skill (Tier 2)

### Key Components

**Resilient API Client** - Handle Binance API with retry logic:

```python
from resilience_patterns import CircuitBreaker, RateLimiter, RetryPolicy

class BinanceAdapter:
    """Resilient Binance API client with circuit breaker"""

    def __init__(self, api_key: str, api_secret: str):
        self.client = BinanceClient(api_key, api_secret)

        # Circuit breaker: open after 5 failures in 60s
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60,
            recovery_timeout=30
        )

        # Rate limiter: 1200 req/min (Binance limit)
        self.rate_limiter = RateLimiter(
            max_requests=1200,
            time_window=60
        )

        # Retry policy: exponential backoff
        self.retry_policy = RetryPolicy(
            max_attempts=3,
            backoff_multiplier=2,
            initial_delay=1,
            max_delay=10,
            retryable_errors=[408, 429, 500, 502, 503, 504]
        )

    @circuit_breaker.protected
    @rate_limiter.limit
    @retry_policy.retry
    async def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float = None
    ) -> Order:
        """Place order with resilience patterns"""

        try:
            # Add timestamp and signature
            order_params = self._prepare_order_params(
                symbol, side, order_type, quantity, price
            )

            response = await self.client.post(
                "/api/v3/order",
                data=order_params
            )

            return Order.from_api_response(response)

        except BinanceAPIException as e:
            # Handle specific Binance errors
            if e.code == -2010:  # Insufficient balance
                raise InsufficientBalanceError(e.message)
            elif e.code == -1013:  # Invalid quantity
                raise InvalidOrderError(e.message)
            else:
                raise ExchangeAPIError(f"Binance error: {e.message}")

    async def get_account_balance(self) -> dict[str, float]:
        """Get account balances with caching"""

        cache_key = "account_balance"
        cached = await self.cache.get(cache_key)

        if cached:
            return cached

        response = await self.client.get("/api/v3/account")
        balances = {
            asset["asset"]: float(asset["free"])
            for asset in response["balances"]
            if float(asset["free"]) > 0
        }

        await self.cache.set(cache_key, balances, ttl=5)  # Cache 5s
        return balances
```

**WebSocket Manager** - Real-time market data:

```python
class BinanceWebSocketManager:
    """Manage Binance WebSocket connections with reconnection"""

    def __init__(self):
        self.connections = {}
        self.reconnect_delay = 5
        self.max_reconnect_attempts = 10

    async def subscribe_ticker(
        self,
        symbol: str,
        callback: Callable
    ):
        """Subscribe to real-time ticker updates"""

        stream = f"{symbol.lower()}@ticker"

        while True:
            try:
                async with websockets.connect(
                    f"wss://stream.binance.com:9443/ws/{stream}"
                ) as ws:
                    self.connections[symbol] = ws

                    async for message in ws:
                        data = json.loads(message)
                        await callback(TickerData.from_websocket(data))

            except websockets.ConnectionClosed:
                logger.warning(f"WebSocket closed for {symbol}, reconnecting...")
                await asyncio.sleep(self.reconnect_delay)
            except Exception as e:
                logger.error(f"WebSocket error for {symbol}: {e}")
                await asyncio.sleep(self.reconnect_delay)
```

### Crypto-Specific Considerations

- **Rate Limiting:** Binance has strict limits (1200 req/min, order limits per symbol)
- **Timestamp Sync:** Binance requires timestamp within 5000ms, implement NTP sync
- **IP Whitelisting:** Production systems should use IP whitelisting for security
- **Order Filters:** Validate against symbol filters (LOT_SIZE, PRICE_FILTER, MIN_NOTIONAL)

### Design Patterns

- **Adapter Pattern:** Abstract Binance-specific details behind common interface
- **Decorator Pattern:** Add resilience through circuit breaker, retry decorators
- **Proxy Pattern:** WebSocket manager proxies connections with auto-reconnect

### Test Coverage Requirements

- **Unit Tests (90%):** Mock Binance responses, test error handling
- **Integration Tests (80%):** Test against Binance Testnet
- **Failure Tests:** Simulate network failures, API errors, rate limits

**Test Example:**

```python
@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_failures():
    """Circuit breaker should open after consecutive failures"""

    adapter = BinanceAdapter(api_key="test", api_secret="test")

    # Mock Binance API to return 500 errors
    with patch.object(adapter.client, 'post') as mock_post:
        mock_post.side_effect = BinanceAPIException("Server error", 500)

        # First 5 failures should attempt requests
        for i in range(5):
            with pytest.raises(ExchangeAPIError):
                await adapter.place_order("BTCUSDT", "BUY", "LIMIT", 0.001, 45000)

        # Circuit breaker should now be open
        assert adapter.circuit_breaker.is_open()

        # 6th request should fail fast without calling API
        with pytest.raises(CircuitBreakerOpenError):
            await adapter.place_order("BTCUSDT", "BUY", "LIMIT", 0.001, 45000)

        # Verify API was only called 5 times (circuit breaker blocked 6th)
        assert mock_post.call_count == 5
```

## 3. Trading Strategy Layer

**Responsibility:** Implement risk management rules, position sizing algorithms, portfolio rebalancing, and P&L tracking.

### Key Components

**Risk Manager** - Enforce trading limits and risk controls:

```python
class RiskManager:
    """Enforce risk management rules"""

    def __init__(self, config: RiskConfig):
        self.config = config
        self.portfolio_tracker = PortfolioTracker()

    def validate_trade(
        self,
        trade: TradeIntent,
        portfolio: Portfolio
    ) -> RiskAssessment:
        """Validate trade against risk limits"""

        checks = {
            "position_size": self._check_position_size(trade, portfolio),
            "max_drawdown": self._check_max_drawdown(portfolio),
            "concentration": self._check_concentration(trade, portfolio),
            "leverage": self._check_leverage(trade, portfolio),
            "correlation": self._check_correlation(trade, portfolio),
            "volatility": self._check_volatility(trade),
            "liquidity": self._check_liquidity(trade)
        }

        passed = all(checks.values())

        return RiskAssessment(
            approved=passed,
            checks=checks,
            risk_score=self._calculate_risk_score(checks),
            recommendations=self._generate_recommendations(checks)
        )

    def _check_position_size(
        self,
        trade: TradeIntent,
        portfolio: Portfolio
    ) -> bool:
        """Ensure position doesn't exceed max % of portfolio"""

        position_value = trade.quantity * trade.price
        max_position = portfolio.total_value * self.config.max_position_pct

        return position_value <= max_position

    def _check_max_drawdown(self, portfolio: Portfolio) -> bool:
        """Ensure current drawdown doesn't exceed limit"""

        current_drawdown = (
            (portfolio.peak_value - portfolio.current_value)
            / portfolio.peak_value
        )

        return current_drawdown <= self.config.max_drawdown_pct
```

**Position Sizer** - Calculate optimal position sizes:

```python
class PositionSizer:
    """Calculate position sizes using Kelly Criterion and risk-based sizing"""

    def calculate_position_size(
        self,
        signal_strength: float,  # 0.0 to 1.0
        portfolio_value: float,
        risk_per_trade: float = 0.02,  # 2% risk per trade
        win_rate: float = 0.55,
        avg_win_loss_ratio: float = 1.5
    ) -> float:
        """Calculate position size using Kelly Criterion with scaling"""

        # Kelly Criterion: f* = (p * b - q) / b
        # where p = win rate, q = loss rate, b = win/loss ratio
        kelly_pct = (
            (win_rate * avg_win_loss_ratio - (1 - win_rate))
            / avg_win_loss_ratio
        )

        # Scale Kelly by signal strength and use fractional Kelly (0.25)
        kelly_fraction = 0.25
        adjusted_pct = kelly_pct * kelly_fraction * signal_strength

        # Cap at risk per trade limit
        final_pct = min(adjusted_pct, risk_per_trade)

        return portfolio_value * final_pct
```

**P&L Tracker** - Track performance and generate reports:

```python
class PnLTracker:
    """Track profit/loss and performance metrics"""

    def __init__(self, storage: Storage):
        self.storage = storage
        self.trades = []

    async def record_trade(self, trade: ExecutedTrade):
        """Record completed trade"""
        self.trades.append(trade)
        await self.storage.save_trade(trade)

    def calculate_metrics(self, period: str = "30d") -> PerformanceMetrics:
        """Calculate performance metrics"""

        period_trades = self._get_trades_for_period(period)

        return PerformanceMetrics(
            total_return=self._calculate_total_return(period_trades),
            sharpe_ratio=self._calculate_sharpe_ratio(period_trades),
            max_drawdown=self._calculate_max_drawdown(period_trades),
            win_rate=self._calculate_win_rate(period_trades),
            profit_factor=self._calculate_profit_factor(period_trades),
            avg_trade_duration=self._calculate_avg_duration(period_trades),
            num_trades=len(period_trades)
        )
```

### Crypto-Specific Considerations

- **Liquidation Risk:** For leveraged positions, calculate liquidation price and maintain buffer
- **Funding Rates:** For perpetuals, account for positive/negative funding in P&L calculations
- **Gas Costs:** For DeFi, deduct gas fees from expected profit (can be 10-50% on small trades)
- **Impermanent Loss:** For liquidity provision, track IL alongside trading P&L

### Design Patterns

- **Strategy Pattern:** Multiple risk management strategies (conservative, moderate, aggressive)
- **Template Method:** Common P&L calculation with exchange-specific implementations
- **Observer Pattern:** Notify systems when risk limits breached

### Test Coverage Requirements

- **Unit Tests (95%):** Test each risk check, position sizing algorithm independently
- **Property Tests:** Use hypothesis to test risk rules across wide range of inputs
- **Integration Tests (85%):** Test full trade validation → execution → P&L flow

**Test Example:**

```python
def test_position_sizer_respects_risk_limit():
    """Position sizer should never exceed max risk per trade"""

    sizer = PositionSizer()
    portfolio_value = 100000
    max_risk = 0.02  # 2%

    # Test across range of signal strengths
    for signal_strength in [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
        position_value = sizer.calculate_position_size(
            signal_strength=signal_strength,
            portfolio_value=portfolio_value,
            risk_per_trade=max_risk
        )

        # Position should never exceed 2% of portfolio
        assert position_value <= portfolio_value * max_risk

        # Position should scale with signal strength
        if signal_strength > 0.5:
            assert position_value > portfolio_value * max_risk * 0.5
```

## 4. Data Pipeline Layer

**Responsibility:** Ingest, validate, transform, and cache market data from multiple sources with low-latency delivery.

### Key Components

**Data Ingestion Service** - Collect data from multiple sources:

```python
class MarketDataIngestion:
    """Ingest and normalize market data from multiple sources"""

    def __init__(self, sources: list[DataSource]):
        self.sources = sources
        self.redis = Redis()
        self.validator = DataValidator()

    async def start_ingestion(self):
        """Start ingesting data from all sources"""

        tasks = [
            self._ingest_from_source(source)
            for source in self.sources
        ]

        await asyncio.gather(*tasks)

    async def _ingest_from_source(self, source: DataSource):
        """Ingest data from single source with validation"""

        async for raw_data in source.stream():
            try:
                # Validate data quality
                validation = self.validator.validate(raw_data)

                if not validation.passed:
                    logger.warning(
                        f"Invalid data from {source.name}: {validation.errors}"
                    )
                    continue

                # Normalize to common format
                normalized = self._normalize_data(raw_data, source.format)

                # Cache in Redis with TTL
                await self.redis.set(
                    f"market:{normalized.symbol}:ticker",
                    normalized.to_json(),
                    ex=10  # 10s TTL
                )

                # Publish to subscribers
                await self.redis.publish(
                    f"market:{normalized.symbol}",
                    normalized.to_json()
                )

            except Exception as e:
                logger.error(f"Error ingesting from {source.name}: {e}")
```

**Data Validator** - Ensure data quality:

```python
class DataValidator:
    """Validate market data quality"""

    def validate(self, data: dict) -> ValidationResult:
        """Run validation checks on market data"""

        checks = [
            self._check_required_fields(data),
            self._check_price_sanity(data),
            self._check_timestamp_freshness(data),
            self._check_volume_sanity(data),
            self._check_spread_sanity(data)
        ]

        return ValidationResult(
            passed=all(check.passed for check in checks),
            errors=[check.error for check in checks if not check.passed]
        )

    def _check_price_sanity(self, data: dict) -> Check:
        """Detect anomalous price movements"""

        symbol = data["symbol"]
        current_price = data["price"]

        # Get last known price from cache
        last_price = self._get_cached_price(symbol)

        if last_price:
            change_pct = abs(current_price - last_price) / last_price

            # Flag if price changed >20% in one tick
            if change_pct > 0.20:
                return Check(
                    passed=False,
                    error=f"Anomalous price change: {change_pct:.2%}"
                )

        return Check(passed=True)
```

**Cache Manager** - Intelligent caching strategy:

```python
class CacheManager:
    """Manage market data caching with intelligent TTLs"""

    def __init__(self, redis: Redis):
        self.redis = redis

        # Different TTLs for different data types
        self.ttls = {
            "ticker": 5,        # 5s for real-time ticker
            "orderbook": 2,     # 2s for orderbook
            "trades": 10,       # 10s for recent trades
            "klines": 60,       # 60s for candlestick data
            "account": 5        # 5s for account data
        }

    async def get_or_fetch(
        self,
        key: str,
        data_type: str,
        fetch_fn: Callable
    ) -> dict:
        """Get from cache or fetch if missing/stale"""

        cached = await self.redis.get(key)

        if cached:
            return json.loads(cached)

        # Cache miss, fetch fresh data
        data = await fetch_fn()

        await self.redis.set(
            key,
            json.dumps(data),
            ex=self.ttls[data_type]
        )

        return data
```

### Crypto-Specific Considerations

- **Data Freshness:** Crypto moves fast, stale data (>5s) can cause bad trades
- **Exchange Downtime:** Have fallback data sources when primary exchange down
- **Data Conflicts:** Handle conflicting prices from different exchanges (use median/weighted avg)
- **Historical Data:** Store tick data for backtesting and strategy optimization

### Design Patterns

- **Publisher-Subscriber:** Redis pub/sub for real-time data distribution
- **Cache-Aside Pattern:** Check cache first, fetch on miss
- **Pipeline Pattern:** Data flows through validation → normalization → caching → distribution

### Test Coverage Requirements

- **Unit Tests (90%):** Test each validator check, normalization logic
- **Integration Tests (85%):** Test full ingestion → validation → caching → distribution
- **Performance Tests:** Ensure <10ms latency for cache hits, <100ms for cache misses

**Test Example:**

```python
@pytest.mark.asyncio
async def test_data_validator_rejects_stale_data():
    """Validator should reject data with old timestamps"""

    validator = DataValidator()

    # Data with timestamp 1 hour old
    stale_data = {
        "symbol": "BTCUSDT",
        "price": 45000,
        "timestamp": int(time.time() - 3600) * 1000,  # 1h ago
        "volume": 1000000
    }

    result = validator.validate(stale_data)

    assert result.passed is False
    assert "stale" in result.errors[0].lower() or "timestamp" in result.errors[0].lower()
```

## 5. Monitoring & Observability Layer

**Responsibility:** Collect metrics, logs, traces, and alerts for production system health and debugging.

### Key Components

**Metrics Collector** - Gather system and trading metrics:

```python
from prometheus_client import Counter, Histogram, Gauge

class MetricsCollector:
    """Collect and expose Prometheus metrics"""

    def __init__(self):
        # Trading metrics
        self.trades_total = Counter(
            "crypto_agent_trades_total",
            "Total number of trades executed",
            ["symbol", "side", "status"]
        )

        self.trade_value = Histogram(
            "crypto_agent_trade_value_usd",
            "Trade value in USD",
            ["symbol"],
            buckets=[10, 50, 100, 500, 1000, 5000, 10000]
        )

        self.portfolio_value = Gauge(
            "crypto_agent_portfolio_value_usd",
            "Current portfolio value in USD"
        )

        # System metrics
        self.api_latency = Histogram(
            "crypto_agent_api_latency_seconds",
            "Exchange API latency",
            ["exchange", "endpoint"],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
        )

        self.consensus_confidence = Histogram(
            "crypto_agent_consensus_confidence",
            "LLM consensus confidence scores",
            buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0]
        )

        self.errors_total = Counter(
            "crypto_agent_errors_total",
            "Total number of errors",
            ["component", "error_type"]
        )

    def record_trade(self, trade: ExecutedTrade):
        """Record trade execution metrics"""
        self.trades_total.labels(
            symbol=trade.symbol,
            side=trade.side,
            status=trade.status
        ).inc()

        self.trade_value.labels(
            symbol=trade.symbol
        ).observe(trade.value_usd)

    def record_api_call(self, exchange: str, endpoint: str, duration: float):
        """Record API call latency"""
        self.api_latency.labels(
            exchange=exchange,
            endpoint=endpoint
        ).observe(duration)
```

**Alert Manager** - Define and trigger alerts:

```python
class AlertManager:
    """Manage alerts for critical events"""

    def __init__(self, notifiers: list[Notifier]):
        self.notifiers = notifiers
        self.alert_rules = self._define_alert_rules()

    def _define_alert_rules(self) -> list[AlertRule]:
        """Define alert rules"""
        return [
            AlertRule(
                name="HighDrawdown",
                condition=lambda metrics: metrics.drawdown > 0.10,
                severity=AlertSeverity.CRITICAL,
                message="Portfolio drawdown exceeded 10%"
            ),
            AlertRule(
                name="ConsecutiveLosses",
                condition=lambda metrics: metrics.consecutive_losses >= 5,
                severity=AlertSeverity.HIGH,
                message="5 consecutive losing trades"
            ),
            AlertRule(
                name="APILatency",
                condition=lambda metrics: metrics.api_latency_p95 > 2.0,
                severity=AlertSeverity.MEDIUM,
                message="API latency P95 > 2s"
            ),
            AlertRule(
                name="LowConsensusConfidence",
                condition=lambda metrics: metrics.avg_consensus_confidence < 0.6,
                severity=AlertSeverity.MEDIUM,
                message="Average consensus confidence < 60%"
            )
        ]

    async def check_and_alert(self, metrics: SystemMetrics):
        """Check alert rules and notify"""

        for rule in self.alert_rules:
            if rule.condition(metrics):
                alert = Alert(
                    rule=rule.name,
                    severity=rule.severity,
                    message=rule.message,
                    metrics_snapshot=metrics,
                    timestamp=datetime.utcnow()
                )

                await self._send_alert(alert)

    async def _send_alert(self, alert: Alert):
        """Send alert to all notifiers"""
        tasks = [
            notifier.send(alert)
            for notifier in self.notifiers
        ]
        await asyncio.gather(*tasks)
```

**Structured Logger** - Contextual logging:

```python
import structlog

class TradingLogger:
    """Structured logging for crypto trading agent"""

    def __init__(self):
        self.logger = structlog.get_logger()

    def log_trade_decision(
        self,
        decision: TradeDecision,
        market_data: dict,
        portfolio: dict
    ):
        """Log trading decision with full context"""

        self.logger.info(
            "trade_decision",
            action=decision.action,
            confidence=decision.confidence,
            symbol=market_data["symbol"],
            price=market_data["price"],
            portfolio_value=portfolio["total_value"],
            reasoning=decision.reasoning,
            llm_votes=decision.votes
        )

    def log_trade_execution(
        self,
        trade: ExecutedTrade,
        latency_ms: float
    ):
        """Log trade execution"""

        self.logger.info(
            "trade_executed",
            trade_id=trade.id,
            symbol=trade.symbol,
            side=trade.side,
            quantity=trade.quantity,
            price=trade.price,
            status=trade.status,
            latency_ms=latency_ms
        )

    def log_error(
        self,
        component: str,
        error: Exception,
        context: dict
    ):
        """Log error with context"""

        self.logger.error(
            "error_occurred",
            component=component,
            error_type=type(error).__name__,
            error_message=str(error),
            **context
        )
```

### Crypto-Specific Considerations

- **Real-Time Dashboards:** Use Grafana to visualize portfolio value, P&L, positions in real-time
- **Audit Trail:** Log every trade decision and execution for compliance and debugging
- **Performance Attribution:** Track which strategies/LLMs contribute most to P&L
- **Slippage Monitoring:** Track expected vs actual execution prices

### Design Patterns

- **Observer Pattern:** Components register to receive metrics updates
- **Singleton Pattern:** Single metrics collector instance across application
- **Facade Pattern:** Simple interface to complex monitoring stack (Prometheus + Grafana + AlertManager)

### Test Coverage Requirements

- **Unit Tests (90%):** Test metric recording, alert rule evaluation
- **Integration Tests (85%):** Test full metrics → Prometheus → Grafana pipeline
- **Alert Tests:** Verify alerts trigger correctly under failure conditions

**Test Example:**

```python
def test_alert_triggers_on_high_drawdown():
    """Alert should trigger when drawdown exceeds threshold"""

    alert_manager = AlertManager(notifiers=[MockNotifier()])

    # Metrics with high drawdown
    metrics = SystemMetrics(
        drawdown=0.15,  # 15% drawdown
        consecutive_losses=2,
        api_latency_p95=0.5,
        avg_consensus_confidence=0.75
    )

    # Should trigger HighDrawdown alert
    triggered_alerts = alert_manager.check_and_alert(metrics)

    assert len(triggered_alerts) == 1
    assert triggered_alerts[0].rule == "HighDrawdown"
    assert triggered_alerts[0].severity == AlertSeverity.CRITICAL
```

## Testing Strategy

### Unit Tests (Target: 90%+ coverage)

Test each component in isolation with mocked dependencies:

```bash
# Run unit tests with coverage
pytest tests/unit/ --cov=src --cov-report=html --cov-report=term

# Coverage breakdown by layer
pytest tests/unit/ --cov=src --cov-report=term --cov-report=json
```

**Key areas to test:**
- Consensus voting logic with various LLM response patterns
- Risk rule validation with edge cases (zero balance, max drawdown, etc.)
- Position sizing algorithms with property-based testing
- Data validation with malformed/anomalous data
- Alert rule evaluation with threshold boundary conditions

### Integration Tests (Target: 80%+ coverage)

Test interactions between layers using test containers:

```python
import pytest
from testcontainers.redis import RedisContainer
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def test_infrastructure():
    """Spin up test infrastructure"""

    with RedisContainer() as redis, \
         PostgresContainer() as postgres:

        yield {
            "redis_url": redis.get_connection_url(),
            "postgres_url": postgres.get_connection_url()
        }

@pytest.mark.integration
async def test_full_trading_cycle(test_infrastructure):
    """Test full cycle: market data → consensus → risk check → execution → monitoring"""

    # Setup agent with test infrastructure
    agent = CryptoAgent(
        redis_url=test_infrastructure["redis_url"],
        postgres_url=test_infrastructure["postgres_url"],
        binance_testnet=True
    )

    # Inject test market data
    await agent.data_pipeline.inject_test_data({
        "symbol": "BTCUSDT",
        "price": 45000,
        "change_24h": 5.5,
        "volume_24h": 1_000_000_000
    })

    # Trigger trading cycle
    result = await agent.run_trading_cycle()

    # Verify full cycle executed
    assert result.consensus_reached is True
    assert result.risk_check_passed is True
    assert result.trade_executed is True
    assert result.metrics_recorded is True
```

### End-to-End Tests

Test against real Binance Testnet:

```python
@pytest.mark.e2e
@pytest.mark.slow
async def test_real_binance_testnet_integration():
    """Test against real Binance Testnet API"""

    agent = CryptoAgent(
        binance_api_key=os.environ["BINANCE_TESTNET_KEY"],
        binance_api_secret=os.environ["BINANCE_TESTNET_SECRET"],
        binance_testnet=True
    )

    # Place real test order
    order = await agent.place_market_order(
        symbol="BTCUSDT",
        side="BUY",
        quantity=0.001
    )

    assert order.status == "FILLED"
    assert order.executed_qty == 0.001
```

### Performance Tests

Ensure system meets latency requirements:

```python
import pytest
from locust import HttpUser, task, between

class TradingAgentLoadTest(HttpUser):
    """Load test trading agent API"""

    wait_time = between(1, 2)

    @task
    def get_portfolio(self):
        self.client.get("/api/portfolio")

    @task
    def get_market_data(self):
        self.client.get("/api/market/BTCUSDT")

    @task(3)
    def place_order(self):
        self.client.post("/api/orders", json={
            "symbol": "BTCUSDT",
            "side": "BUY",
            "quantity": 0.001
        })

# Run load test
# locust -f tests/performance/load_test.py --headless -u 100 -r 10 -t 60s
```

## Integration with Other Skills

### With `consensus-engine` (Tier 2)

```python
from consensus_engine import ConsensusEngine, VotingStrategy

# Use consensus engine for LLM voting
consensus = ConsensusEngine(
    models=["gpt-4", "claude-3-opus", "gemini-pro"],
    strategy=VotingStrategy.WEIGHTED,  # Weight by historical accuracy
    confidence_threshold=0.75
)

result = await consensus.get_consensus(
    prompt=trading_prompt,
    response_format={"decision": "BUY|SELL|HOLD", "reasoning": "string"}
)
```

### With `resilience-patterns` (Tier 2)

```python
from resilience_patterns import CircuitBreaker, RetryPolicy, RateLimiter

# Apply resilience patterns to Binance adapter
@circuit_breaker.protected(failure_threshold=5, timeout=60)
@retry_policy.retry(max_attempts=3, backoff_multiplier=2)
@rate_limiter.limit(max_requests=1200, time_window=60)
async def place_order(symbol: str, side: str, quantity: float):
    return await binance_client.place_order(symbol, side, quantity)
```

### With `mcp-builder` (Tier 1)

Create MCP server to expose trading agent capabilities:

```python
from mcp_builder import MCPServer, Tool

server = MCPServer("crypto-trading-agent")

@server.tool()
async def get_portfolio_value() -> float:
    """Get current portfolio value"""
    portfolio = await agent.get_portfolio()
    return portfolio.total_value

@server.tool()
async def execute_trade(
    symbol: str,
    side: str,
    quantity: float
) -> dict:
    """Execute a trade"""
    result = await agent.execute_trade(symbol, side, quantity)
    return result.to_dict()
```

### With `agent-testing-framework` (Tier 2)

```python
from agent_testing_framework import AgentTestSuite, Scenario

# Create test suite for trading agent
suite = AgentTestSuite(agent=crypto_agent)

# Add test scenarios
suite.add_scenario(
    Scenario(
        name="bull_market_trading",
        market_conditions={"trend": "bullish", "volatility": "low"},
        expected_behavior={"trades_per_hour": ">5", "win_rate": ">0.55"}
    )
)

# Run tests
results = await suite.run()
assert results.pass_rate > 0.90
```

## Project Initialization

Use the scaffolding script to create a new crypto trading agent project:

```bash
# Initialize new crypto trading agent project
python scripts/init_crypto_agent.py \
  --name my-trading-bot \
  --exchange binance \
  --strategies momentum,mean-reversion \
  --llm-providers openai,anthropic \
  --output ./my-trading-bot

# This creates:
# my-trading-bot/
# ├── src/
# │   ├── consensus/        # Layer 1: Smart Consensus
# │   ├── adapters/         # Layer 2: Exchange Adapters
# │   ├── strategies/       # Layer 3: Trading Strategies
# │   ├── data/            # Layer 4: Data Pipeline
# │   └── monitoring/      # Layer 5: Observability
# ├── tests/
# │   ├── unit/
# │   ├── integration/
# │   └── e2e/
# ├── config/
# │   ├── risk_rules.yaml
# │   ├── exchanges.yaml
# │   └── monitoring.yaml
# ├── docker-compose.yml   # Redis, Postgres, Grafana
# └── pyproject.toml
```

Validate architecture compliance:

```bash
# Validate project follows 5-layer architecture
python scripts/validate_architecture.py ./my-trading-bot

# Output:
# ✅ Layer 1 (Smart Consensus): consensus/ exists, implements ConsensusEngine
# ✅ Layer 2 (Binance Adapter): adapters/ exists, implements resilience patterns
# ✅ Layer 3 (Trading Strategy): strategies/ exists, implements RiskManager
# ✅ Layer 4 (Data Pipeline): data/ exists, implements caching
# ✅ Layer 5 (Monitoring): monitoring/ exists, exposes Prometheus metrics
# ✅ Test coverage: 87% (target: 80%+)
# ✅ All layers properly integrated
```

## Resources

### scripts/

- **init_crypto_agent.py** - Scaffold new crypto trading agent project with 5-layer architecture
- **validate_architecture.py** - Validate project structure and architecture compliance

### references/

- **binance_api_guide.md** - Binance API specifics (rate limits, order filters, error codes)
- **crypto_risk_patterns.md** - Crypto-specific risk management patterns (liquidation, MEV, gas)
- **defi_integration.md** - DeFi protocol integration guide (Uniswap, Aave, dYdX)

### assets/

- **crypto-agent-template/** - FastAPI project boilerplate with 5-layer architecture pre-configured

## Production Checklist

Before deploying to production:

- [ ] **Layer 1:** Multi-LLM consensus with ≥3 models, confidence threshold ≥0.75
- [ ] **Layer 2:** Circuit breaker, retry policy, rate limiter implemented
- [ ] **Layer 3:** Risk rules enforced (max drawdown, position size, leverage limits)
- [ ] **Layer 4:** Data validation pipeline with anomaly detection
- [ ] **Layer 5:** Prometheus metrics, Grafana dashboards, PagerDuty alerts
- [ ] **Testing:** ≥80% test coverage, load tests pass at 100 RPS
- [ ] **Security:** API keys in secrets manager, IP whitelisting enabled
- [ ] **Compliance:** Audit trail logging, regulatory compliance checks
- [ ] **Documentation:** Runbooks for common failures, architecture diagram
- [ ] **Disaster Recovery:** Backup strategy, rollback procedures, kill switch

## Common Patterns

### Kill Switch

Implement emergency stop for runaway losses:

```python
class KillSwitch:
    """Emergency stop for trading agent"""

    def __init__(self, max_drawdown: float = 0.15):
        self.max_drawdown = max_drawdown
        self.activated = False

    def check(self, portfolio: Portfolio):
        """Check if kill switch should activate"""

        if portfolio.drawdown >= self.max_drawdown:
            self.activate("Max drawdown exceeded")

    def activate(self, reason: str):
        """Activate kill switch - stop all trading"""

        self.activated = True
        logger.critical(f"KILL SWITCH ACTIVATED: {reason}")

        # Close all positions
        await self.close_all_positions()

        # Disable trading
        await self.disable_trading()

        # Alert all channels
        await self.alert_manager.send_critical_alert(
            f"Trading halted: {reason}"
        )
```

### Paper Trading Mode

Test strategies without real money:

```python
class PaperTradingAdapter:
    """Simulate trades without executing on exchange"""

    def __init__(self, initial_balance: float = 100000):
        self.balance = initial_balance
        self.positions = {}
        self.trades = []

    async def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float
    ) -> Order:
        """Simulate order execution"""

        # Simulate slippage (0.1%)
        slippage = 0.001
        execution_price = price * (1 + slippage if side == "BUY" else 1 - slippage)

        # Update simulated balance
        cost = quantity * execution_price
        if side == "BUY":
            self.balance -= cost
        else:
            self.balance += cost

        # Record trade
        trade = SimulatedTrade(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=execution_price,
            timestamp=datetime.utcnow()
        )
        self.trades.append(trade)

        return Order.from_simulated_trade(trade)
```

### Strategy Backtesting

Backtest strategies on historical data:

```python
class Backtester:
    """Backtest trading strategies on historical data"""

    async def run_backtest(
        self,
        strategy: TradingStrategy,
        historical_data: pd.DataFrame,
        initial_balance: float = 100000
    ) -> BacktestResults:
        """Run backtest simulation"""

        portfolio = PaperPortfolio(initial_balance)

        for timestamp, market_data in historical_data.iterrows():
            # Get strategy signal
            signal = await strategy.generate_signal(market_data)

            # Execute trade in paper portfolio
            if signal.action != "HOLD":
                await portfolio.execute_trade(
                    symbol=signal.symbol,
                    side=signal.action,
                    quantity=signal.quantity,
                    price=market_data["close"]
                )

        # Calculate performance metrics
        return BacktestResults(
            total_return=portfolio.calculate_return(),
            sharpe_ratio=portfolio.calculate_sharpe(),
            max_drawdown=portfolio.max_drawdown,
            trades=portfolio.trades
        )
```

## Support

For issues or questions:
- Review reference docs in `references/`
- Check example templates in `assets/crypto-agent-template/`
- Validate architecture with `scripts/validate_architecture.py`
- Refer to Tier 2 skills: `consensus-engine`, `resilience-patterns`, `agent-testing-framework`
