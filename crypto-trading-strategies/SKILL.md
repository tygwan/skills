---
name: crypto-trading-strategies
description: Implement production-grade crypto trading strategies (Arbitrage, Market Making, Momentum, Mean Reversion, Grid Trading) with backtesting, risk controls, and crypto-specific optimizations. Use when building algorithmic trading systems, automated trading bots, or strategy portfolios for CEX/DEX. Includes gas fee optimization, slippage protection, MEV awareness, and integration with crypto-agent-architect Trading Strategy Layer.
---

# Crypto Trading Strategies

## Overview

Production-grade implementations of 5 core cryptocurrency trading strategies with comprehensive backtesting, risk controls, and crypto-specific optimizations. Each strategy includes algorithm details, implementation guidelines, performance metrics, and integration with the crypto-agent-architect framework.

**Use this skill when:**
- Implementing automated trading strategies for crypto markets
- Building multi-strategy trading systems with portfolio allocation
- Backtesting trading algorithms on historical crypto data
- Optimizing strategies for gas fees, slippage, and liquidity constraints
- Integrating trading logic with crypto-agent-architect Layer 3 (Trading Strategy)

## Strategy Overview

| Strategy | Type | Timeframe | Complexity | Risk | Profit Potential |
|----------|------|-----------|------------|------|------------------|
| **Arbitrage** | Market-neutral | Seconds-Minutes | Low | Low | Low-Medium (1-3%) |
| **Market Making** | Liquidity provision | Continuous | Medium | Medium | Medium (5-15%) |
| **Momentum** | Trend-following | Hours-Days | Low | High | High (20-50%) |
| **Mean Reversion** | Contrarian | Hours-Days | Medium | Medium | Medium (10-30%) |
| **Grid Trading** | Range-bound | Days-Weeks | Low | Medium | Medium (15-40%) |

## 1. Arbitrage Strategy

### Concept

Exploit price differences for the same asset across different exchanges or trading pairs. Profit from market inefficiencies with near-zero directional risk.

**Types:**
- **Spatial Arbitrage:** Price differences between exchanges (e.g., BTC/USDT on Binance vs Coinbase)
- **Triangular Arbitrage:** Price inefficiencies in currency triplets (e.g., BTC→ETH→USDT→BTC)
- **Statistical Arbitrage:** Mean-reverting pairs trading (e.g., ETH/BTC historical correlation)

### Algorithm

```python
from typing import List, Tuple, Optional
from dataclasses import dataclass
import asyncio

@dataclass
class ArbitrageOpportunity:
    """Represents an arbitrage opportunity"""
    buy_exchange: str
    sell_exchange: str
    symbol: str
    buy_price: float
    sell_price: float
    spread_pct: float
    profit_after_fees: float
    execution_time_ms: float

class ArbitrageStrategy:
    """Spatial arbitrage strategy across multiple exchanges"""

    def __init__(
        self,
        exchanges: List[ExchangeAdapter],
        min_spread_pct: float = 0.5,  # Minimum 0.5% spread
        max_execution_time_ms: float = 3000,  # Max 3s execution
        trade_size_usd: float = 1000
    ):
        self.exchanges = exchanges
        self.min_spread_pct = min_spread_pct
        self.max_execution_time_ms = max_execution_time_ms
        self.trade_size_usd = trade_size_usd

    async def scan_opportunities(
        self,
        symbols: List[str]
    ) -> List[ArbitrageOpportunity]:
        """Scan all exchange pairs for arbitrage opportunities"""

        opportunities = []

        # Fetch prices from all exchanges concurrently
        price_tasks = [
            self._fetch_prices(exchange, symbols)
            for exchange in self.exchanges
        ]
        all_prices = await asyncio.gather(*price_tasks)

        # Compare prices across exchange pairs
        for symbol in symbols:
            for i, exchange_i in enumerate(self.exchanges):
                for j, exchange_j in enumerate(self.exchanges):
                    if i >= j:
                        continue

                    buy_price = all_prices[i].get(symbol)
                    sell_price = all_prices[j].get(symbol)

                    if not buy_price or not sell_price:
                        continue

                    # Calculate spread
                    spread_pct = (sell_price - buy_price) / buy_price * 100

                    if spread_pct > self.min_spread_pct:
                        opportunity = await self._calculate_opportunity(
                            exchange_i,
                            exchange_j,
                            symbol,
                            buy_price,
                            sell_price,
                            spread_pct
                        )

                        if opportunity and opportunity.profit_after_fees > 0:
                            opportunities.append(opportunity)

        return sorted(opportunities, key=lambda x: x.profit_after_fees, reverse=True)

    async def _calculate_opportunity(
        self,
        buy_exchange: ExchangeAdapter,
        sell_exchange: ExchangeAdapter,
        symbol: str,
        buy_price: float,
        sell_price: float,
        spread_pct: float
    ) -> Optional[ArbitrageOpportunity]:
        """Calculate net profit after fees and execution costs"""

        # Calculate fees
        buy_fee_pct = buy_exchange.get_maker_fee(symbol)
        sell_fee_pct = sell_exchange.get_taker_fee(symbol)
        total_fee_pct = buy_fee_pct + sell_fee_pct

        # Calculate slippage (estimate based on order book depth)
        buy_slippage = await self._estimate_slippage(
            buy_exchange, symbol, self.trade_size_usd, "BUY"
        )
        sell_slippage = await self._estimate_slippage(
            sell_exchange, symbol, self.trade_size_usd, "SELL"
        )

        # Net spread after costs
        net_spread_pct = spread_pct - total_fee_pct - buy_slippage - sell_slippage

        if net_spread_pct <= 0:
            return None

        # Calculate profit
        quantity = self.trade_size_usd / buy_price
        profit_after_fees = quantity * buy_price * (net_spread_pct / 100)

        # Estimate execution time (API latency + order execution)
        execution_time_ms = await self._estimate_execution_time(
            buy_exchange, sell_exchange
        )

        if execution_time_ms > self.max_execution_time_ms:
            return None  # Opportunity may disappear before execution

        return ArbitrageOpportunity(
            buy_exchange=buy_exchange.name,
            sell_exchange=sell_exchange.name,
            symbol=symbol,
            buy_price=buy_price,
            sell_price=sell_price,
            spread_pct=spread_pct,
            profit_after_fees=profit_after_fees,
            execution_time_ms=execution_time_ms
        )

    async def execute_arbitrage(
        self,
        opportunity: ArbitrageOpportunity
    ) -> ArbitrageResult:
        """Execute arbitrage trade atomically"""

        buy_exchange = self._get_exchange(opportunity.buy_exchange)
        sell_exchange = self._get_exchange(opportunity.sell_exchange)
        quantity = self.trade_size_usd / opportunity.buy_price

        try:
            # Execute both legs concurrently
            buy_task = buy_exchange.place_order(
                symbol=opportunity.symbol,
                side="BUY",
                order_type="LIMIT",
                quantity=quantity,
                price=opportunity.buy_price
            )
            sell_task = sell_exchange.place_order(
                symbol=opportunity.symbol,
                side="SELL",
                order_type="LIMIT",
                quantity=quantity,
                price=opportunity.sell_price
            )

            buy_order, sell_order = await asyncio.gather(
                buy_task,
                sell_task,
                return_exceptions=True
            )

            # Handle partial fills or failures
            if isinstance(buy_order, Exception) or isinstance(sell_order, Exception):
                # Rollback: cancel unfilled orders
                await self._rollback_trades(buy_order, sell_order)
                raise ArbitrageExecutionError("Failed to execute both legs")

            actual_profit = self._calculate_actual_profit(buy_order, sell_order)

            return ArbitrageResult(
                success=True,
                expected_profit=opportunity.profit_after_fees,
                actual_profit=actual_profit,
                buy_order=buy_order,
                sell_order=sell_order
            )

        except Exception as e:
            logger.error(f"Arbitrage execution failed: {e}")
            return ArbitrageResult(success=False, error=str(e))
```

### Crypto-Specific Considerations

**Gas Fees (DEX):** For DeFi arbitrage, gas costs can eliminate profits on trades <$5K
```python
def is_profitable_after_gas(profit_usd: float, gas_gwei: int) -> bool:
    """Check if arbitrage profitable after gas fees"""
    gas_cost_usd = (gas_gwei * 200000 * eth_price) / 1e9  # ~200K gas for swap
    return profit_usd > gas_cost_usd * 2  # 2x margin for safety
```

**MEV Protection (DEX):** Use private mempools (Flashbots) to prevent front-running
```python
async def submit_to_flashbots(buy_tx, sell_tx):
    """Submit arbitrage bundle to Flashbots to avoid MEV"""
    bundle = [buy_tx, sell_tx]
    return await flashbots_relay.send_bundle(bundle)
```

**Execution Speed:** Arbitrage opportunities disappear in seconds, optimize latency
- Co-locate servers near exchange data centers
- Use WebSocket feeds instead of REST polling
- Pre-allocate balances on all exchanges

**Triangular Arbitrage:** Detect circular opportunities
```python
def find_triangular_arbitrage(prices: dict) -> Optional[ArbitrageChain]:
    """Find profitable triangular arbitrage (BTC→ETH→USDT→BTC)"""
    btc_eth = prices["BTC/ETH"]
    eth_usdt = prices["ETH/USDT"]
    usdt_btc = prices["USDT/BTC"]

    # Calculate chain profit
    chain_rate = btc_eth * eth_usdt * usdt_btc
    profit_pct = (chain_rate - 1) * 100

    if profit_pct > 0.3:  # >0.3% after fees
        return ArbitrageChain(
            path=["BTC", "ETH", "USDT", "BTC"],
            profit_pct=profit_pct
        )
    return None
```

### Risk Controls

```python
class ArbitrageRiskManager:
    """Risk management for arbitrage strategy"""

    def validate_trade(
        self,
        opportunity: ArbitrageOpportunity,
        portfolio: Portfolio
    ) -> bool:
        """Validate arbitrage trade against risk limits"""

        checks = [
            self._check_balance_sufficient(opportunity, portfolio),
            self._check_spread_not_stale(opportunity),
            self._check_liquidity_adequate(opportunity),
            self._check_execution_time_acceptable(opportunity),
            self._check_counterparty_risk(opportunity)
        ]

        return all(checks)

    def _check_balance_sufficient(
        self,
        opportunity: ArbitrageOpportunity,
        portfolio: Portfolio
    ) -> bool:
        """Ensure sufficient balance on both exchanges"""
        buy_exchange_balance = portfolio.get_balance(opportunity.buy_exchange)
        sell_exchange_balance = portfolio.get_balance(opportunity.sell_exchange)

        required_buy = opportunity.buy_price * quantity
        required_sell = quantity  # Need to own asset to sell

        return (
            buy_exchange_balance >= required_buy and
            sell_exchange_balance >= required_sell
        )

    def _check_spread_not_stale(self, opportunity: ArbitrageOpportunity) -> bool:
        """Reject if price data is stale"""
        age_ms = (datetime.utcnow() - opportunity.timestamp).total_seconds() * 1000
        return age_ms < 1000  # Max 1 second old
```

### Performance Metrics

**Key Metrics:**
- **Win Rate:** 95%+ (most arbitrage trades succeed)
- **Profit per Trade:** 0.5-3% (after fees)
- **Trade Frequency:** 10-50 per day (depends on market volatility)
- **Sharpe Ratio:** 3-5 (low risk, consistent returns)
- **Max Drawdown:** <5% (market-neutral strategy)

### Backtesting

```python
class ArbitrageBacktester:
    """Backtest arbitrage strategy on historical data"""

    async def run_backtest(
        self,
        historical_data: pd.DataFrame,
        exchanges: List[str]
    ) -> BacktestResults:
        """Run backtest simulation"""

        strategy = ArbitrageStrategy(exchanges=exchanges)
        trades = []

        for timestamp, data in historical_data.iterrows():
            # Scan for opportunities at this timestamp
            opportunities = await strategy.scan_opportunities(
                symbols=["BTC/USDT", "ETH/USDT"],
                prices=data
            )

            # Execute best opportunity
            if opportunities:
                best = opportunities[0]
                result = self._simulate_execution(best, data)
                trades.append(result)

        return BacktestResults(
            total_profit=sum(t.profit for t in trades),
            num_trades=len(trades),
            win_rate=sum(1 for t in trades if t.profit > 0) / len(trades),
            sharpe_ratio=self._calculate_sharpe(trades)
        )
```

## 2. Market Making Strategy

### Concept

Provide liquidity by continuously placing buy and sell limit orders around the mid-price. Profit from bid-ask spread while managing inventory risk.

### Algorithm

```python
class MarketMakingStrategy:
    """Market making strategy with inventory management"""

    def __init__(
        self,
        exchange: ExchangeAdapter,
        symbol: str,
        spread_bps: int = 10,  # 10 basis points (0.1%)
        order_size_usd: float = 1000,
        max_inventory_pct: float = 0.5,  # Max 50% inventory skew
        rebalance_threshold_pct: float = 0.3  # Rebalance at 30% skew
    ):
        self.exchange = exchange
        self.symbol = symbol
        self.spread_bps = spread_bps
        self.order_size_usd = order_size_usd
        self.max_inventory_pct = max_inventory_pct
        self.rebalance_threshold_pct = rebalance_threshold_pct

        self.target_inventory = 0.5  # 50% in base, 50% in quote
        self.active_orders = {}

    async def run(self):
        """Main market making loop"""

        while True:
            try:
                # Cancel existing orders
                await self._cancel_all_orders()

                # Get current market state
                ticker = await self.exchange.get_ticker(self.symbol)
                mid_price = (ticker.bid + ticker.ask) / 2

                # Calculate inventory skew
                inventory_skew = await self._calculate_inventory_skew()

                # Adjust quotes based on inventory
                bid_price, ask_price = self._calculate_quotes(
                    mid_price,
                    inventory_skew
                )

                # Place new orders
                await self._place_maker_orders(bid_price, ask_price)

                # Wait for fills or market movement
                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Market making error: {e}")
                await asyncio.sleep(10)

    def _calculate_quotes(
        self,
        mid_price: float,
        inventory_skew: float
    ) -> Tuple[float, float]:
        """Calculate bid/ask prices with inventory adjustment"""

        # Base spread
        half_spread = mid_price * (self.spread_bps / 10000) / 2

        # Inventory adjustment: skew quotes away from excess inventory
        # If too much base asset (>50%), lower both bid/ask to encourage selling
        # If too much quote asset (<50%), raise both bid/ask to encourage buying
        inventory_adjustment = (inventory_skew - 0.5) * mid_price * 0.002  # 0.2% per 10% skew

        bid_price = mid_price - half_spread - inventory_adjustment
        ask_price = mid_price + half_spread - inventory_adjustment

        return bid_price, ask_price

    async def _calculate_inventory_skew(self) -> float:
        """Calculate current inventory position (0=all quote, 1=all base)"""

        balances = await self.exchange.get_account_balance()
        base_asset, quote_asset = self.symbol.split("/")

        base_balance = balances.get(base_asset, 0)
        quote_balance = balances.get(quote_asset, 0)

        # Get mid price to value base in quote terms
        ticker = await self.exchange.get_ticker(self.symbol)
        mid_price = (ticker.bid + ticker.ask) / 2

        base_value = base_balance * mid_price
        total_value = base_value + quote_balance

        if total_value == 0:
            return 0.5  # Neutral if no inventory

        inventory_pct = base_value / total_value
        return inventory_pct

    async def _place_maker_orders(self, bid_price: float, ask_price: float):
        """Place limit orders at bid and ask"""

        quantity = self.order_size_usd / ((bid_price + ask_price) / 2)

        # Place buy order (bid)
        bid_order = await self.exchange.place_order(
            symbol=self.symbol,
            side="BUY",
            order_type="LIMIT",
            quantity=quantity,
            price=bid_price,
            time_in_force="GTC",  # Good till cancel
            post_only=True  # Ensure maker fee
        )
        self.active_orders[bid_order.order_id] = bid_order

        # Place sell order (ask)
        ask_order = await self.exchange.place_order(
            symbol=self.symbol,
            side="SELL",
            order_type="LIMIT",
            quantity=quantity,
            price=ask_price,
            time_in_force="GTC",
            post_only=True
        )
        self.active_orders[ask_order.order_id] = ask_order

    async def _rebalance_inventory(self):
        """Rebalance inventory when skew exceeds threshold"""

        inventory_skew = await self._calculate_inventory_skew()
        deviation = abs(inventory_skew - self.target_inventory)

        if deviation > self.rebalance_threshold_pct:
            # Too much base asset, market sell
            if inventory_skew > self.target_inventory:
                rebalance_qty = await self._calculate_rebalance_quantity(inventory_skew)
                await self.exchange.place_order(
                    symbol=self.symbol,
                    side="SELL",
                    order_type="MARKET",
                    quantity=rebalance_qty
                )
            # Too much quote asset, market buy
            else:
                rebalance_qty = await self._calculate_rebalance_quantity(inventory_skew)
                await self.exchange.place_order(
                    symbol=self.symbol,
                    side="BUY",
                    order_type="MARKET",
                    quantity=rebalance_qty
                )
```

### Crypto-Specific Considerations

**Volatility Management:** Widen spreads during high volatility
```python
def adjust_spread_for_volatility(base_spread_bps: int, volatility: float) -> int:
    """Widen spread when volatility high"""
    volatility_multiplier = 1 + (volatility / 0.02)  # +50% spread per 2% volatility
    return int(base_spread_bps * volatility_multiplier)
```

**Inventory Risk:** Crypto can move 10-20% in minutes, limit inventory exposure
```python
def check_inventory_limits(inventory_pct: float) -> bool:
    """Enforce strict inventory limits"""
    return 0.2 <= inventory_pct <= 0.8  # Max 30% deviation from neutral
```

**Maker vs Taker Fees:** Always use post-only orders to guarantee maker rebates
```python
order = await exchange.place_order(
    symbol="BTC/USDT",
    side="BUY",
    order_type="LIMIT",
    price=bid_price,
    post_only=True,  # Reject if would take liquidity
    time_in_force="GTX"  # Good-Till-Crossing
)
```

**Adverse Selection:** Reduce exposure when consistently filled on one side
```python
class AdverseSelectionDetector:
    """Detect when being adversely selected"""

    def is_adverse_selection(self, recent_fills: List[Fill]) -> bool:
        """Check if fills skewed to one side (sign of informed trading)"""
        if len(recent_fills) < 10:
            return False

        buy_fills = sum(1 for f in recent_fills if f.side == "BUY")
        sell_fills = len(recent_fills) - buy_fills

        # If >70% fills on one side, likely adverse selection
        return max(buy_fills, sell_fills) / len(recent_fills) > 0.7
```

### Performance Metrics

**Key Metrics:**
- **Win Rate:** 80-90% (most trades profitable)
- **Profit per Trade:** 0.1-0.5% (from spread)
- **Trade Frequency:** 50-500 per day (high frequency)
- **Sharpe Ratio:** 1-3 (moderate risk)
- **Max Drawdown:** 10-20% (inventory risk during trends)

## 3. Momentum Strategy

### Concept

Follow trending markets by buying assets showing strong upward momentum and selling those showing weakness. Profits from trend continuation.

### Algorithm

```python
class MomentumStrategy:
    """Momentum trading strategy using multiple timeframes"""

    def __init__(
        self,
        lookback_periods: List[int] = [7, 14, 30],  # Days
        min_momentum_score: float = 0.7,  # 0-1 scale
        position_size_pct: float = 0.10,  # 10% per position
        stop_loss_pct: float = 0.05,  # 5% stop loss
        take_profit_pct: float = 0.15  # 15% take profit
    ):
        self.lookback_periods = lookback_periods
        self.min_momentum_score = min_momentum_score
        self.position_size_pct = position_size_pct
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct

    async def generate_signals(
        self,
        market_data: pd.DataFrame
    ) -> List[TradingSignal]:
        """Generate momentum signals for all symbols"""

        signals = []

        for symbol in market_data["symbol"].unique():
            symbol_data = market_data[market_data["symbol"] == symbol]

            # Calculate momentum score
            momentum_score = self._calculate_momentum_score(symbol_data)

            # Calculate technical indicators
            rsi = self._calculate_rsi(symbol_data, period=14)
            macd, signal_line = self._calculate_macd(symbol_data)

            # Generate signal
            if self._is_buy_signal(momentum_score, rsi, macd, signal_line):
                signals.append(TradingSignal(
                    symbol=symbol,
                    action="BUY",
                    confidence=momentum_score,
                    entry_price=symbol_data["close"].iloc[-1],
                    stop_loss=self._calculate_stop_loss(symbol_data, "BUY"),
                    take_profit=self._calculate_take_profit(symbol_data, "BUY"),
                    reasoning=f"Strong momentum ({momentum_score:.2f}), RSI={rsi:.1f}"
                ))

            elif self._is_sell_signal(momentum_score, rsi, macd, signal_line):
                signals.append(TradingSignal(
                    symbol=symbol,
                    action="SELL",
                    confidence=1 - momentum_score,  # Inverse for bearish
                    entry_price=symbol_data["close"].iloc[-1],
                    stop_loss=self._calculate_stop_loss(symbol_data, "SELL"),
                    take_profit=self._calculate_take_profit(symbol_data, "SELL"),
                    reasoning=f"Weak momentum ({momentum_score:.2f}), RSI={rsi:.1f}"
                ))

        return signals

    def _calculate_momentum_score(self, data: pd.DataFrame) -> float:
        """Calculate composite momentum score from multiple timeframes"""

        scores = []

        for period in self.lookback_periods:
            if len(data) < period:
                continue

            # Calculate return over period
            current_price = data["close"].iloc[-1]
            past_price = data["close"].iloc[-period]
            return_pct = (current_price - past_price) / past_price

            # Normalize to 0-1 scale (assumes -50% to +100% range)
            normalized_score = (return_pct + 0.5) / 1.5
            normalized_score = max(0, min(1, normalized_score))  # Clip to [0,1]

            scores.append(normalized_score)

        # Weighted average (shorter periods weighted higher)
        weights = [2**i for i in range(len(scores))]
        momentum_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)

        return momentum_score

    def _calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate Relative Strength Index"""

        if len(data) < period + 1:
            return 50.0  # Neutral

        deltas = data["close"].diff()
        gains = deltas.where(deltas > 0, 0).rolling(window=period).mean()
        losses = -deltas.where(deltas < 0, 0).rolling(window=period).mean()

        rs = gains / losses
        rsi = 100 - (100 / (1 + rs))

        return rsi.iloc[-1]

    def _calculate_macd(
        self,
        data: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[float, float]:
        """Calculate MACD and signal line"""

        if len(data) < slow + signal:
            return 0.0, 0.0

        ema_fast = data["close"].ewm(span=fast).mean()
        ema_slow = data["close"].ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()

        return macd.iloc[-1], signal_line.iloc[-1]

    def _is_buy_signal(
        self,
        momentum_score: float,
        rsi: float,
        macd: float,
        signal_line: float
    ) -> bool:
        """Determine if conditions met for buy signal"""

        return (
            momentum_score >= self.min_momentum_score and
            rsi > 50 and rsi < 70 and  # Strong but not overbought
            macd > signal_line  # MACD bullish crossover
        )

    def _is_sell_signal(
        self,
        momentum_score: float,
        rsi: float,
        macd: float,
        signal_line: float
    ) -> bool:
        """Determine if conditions met for sell signal"""

        return (
            momentum_score < (1 - self.min_momentum_score) and
            rsi < 50 and rsi > 30 and  # Weak but not oversold
            macd < signal_line  # MACD bearish crossover
        )

    def _calculate_stop_loss(self, data: pd.DataFrame, side: str) -> float:
        """Calculate stop loss level"""

        current_price = data["close"].iloc[-1]

        if side == "BUY":
            return current_price * (1 - self.stop_loss_pct)
        else:  # SELL
            return current_price * (1 + self.stop_loss_pct)

    def _calculate_take_profit(self, data: pd.DataFrame, side: str) -> float:
        """Calculate take profit level"""

        current_price = data["close"].iloc[-1]

        if side == "BUY":
            return current_price * (1 + self.take_profit_pct)
        else:  # SELL
            return current_price * (1 - self.take_profit_pct)
```

### Crypto-Specific Considerations

**24/7 Markets:** Crypto never sleeps, monitor positions continuously
```python
async def monitor_positions_continuously():
    """Monitor positions 24/7 with stop loss checks"""
    while True:
        await check_stop_losses()
        await check_take_profits()
        await asyncio.sleep(30)  # Check every 30s
```

**High Volatility:** Wider stop losses and take profits for crypto
```python
# Traditional stocks: 2-3% stop loss
# Crypto: 5-10% stop loss due to higher volatility
CRYPTO_STOP_LOSS_PCT = 0.07  # 7% stop loss
CRYPTO_TAKE_PROFIT_PCT = 0.20  # 20% take profit (2.86:1 ratio)
```

**Trend Strength Filter:** Only trade strongest trends
```python
def filter_strong_trends(signals: List[TradingSignal]) -> List[TradingSignal]:
    """Only trade signals with confidence >0.8"""
    return [s for s in signals if s.confidence > 0.8]
```

**Alt Season Detection:** Adjust strategy based on market regime
```python
def detect_market_regime(btc_dominance: float) -> str:
    """Detect if in BTC season or alt season"""
    if btc_dominance > 60:
        return "BTC_SEASON"  # Trade BTC only
    elif btc_dominance < 45:
        return "ALT_SEASON"  # Trade alts aggressively
    else:
        return "MIXED"  # Balanced approach
```

### Performance Metrics

**Key Metrics:**
- **Win Rate:** 40-60% (few big winners, many small losers)
- **Profit per Trade:** -5% to +30% (wide distribution)
- **Trade Frequency:** 5-20 per week
- **Sharpe Ratio:** 0.5-2.0 (depends on market regime)
- **Max Drawdown:** 20-40% (high risk strategy)

## 4. Mean Reversion Strategy

### Concept

Profit from price returning to mean after extreme moves. Buy oversold assets, sell overbought assets, expecting reversion to average price.

### Algorithm

```python
class MeanReversionStrategy:
    """Mean reversion strategy using Bollinger Bands and RSI"""

    def __init__(
        self,
        bollinger_period: int = 20,
        bollinger_std: float = 2.0,
        rsi_period: int = 14,
        rsi_oversold: int = 30,
        rsi_overbought: int = 70,
        position_size_pct: float = 0.15,
        mean_reversion_target: float = 0.05  # 5% profit target
    ):
        self.bollinger_period = bollinger_period
        self.bollinger_std = bollinger_std
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.position_size_pct = position_size_pct
        self.mean_reversion_target = mean_reversion_target

    async def generate_signals(
        self,
        market_data: pd.DataFrame
    ) -> List[TradingSignal]:
        """Generate mean reversion signals"""

        signals = []

        for symbol in market_data["symbol"].unique():
            symbol_data = market_data[market_data["symbol"] == symbol]

            # Calculate Bollinger Bands
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(
                symbol_data
            )

            # Calculate RSI
            rsi = self._calculate_rsi(symbol_data)

            current_price = symbol_data["close"].iloc[-1]

            # Buy signal: price below lower BB + RSI oversold
            if current_price < bb_lower and rsi < self.rsi_oversold:
                signals.append(TradingSignal(
                    symbol=symbol,
                    action="BUY",
                    confidence=self._calculate_reversion_confidence(
                        current_price, bb_middle, bb_lower, rsi, "BUY"
                    ),
                    entry_price=current_price,
                    take_profit=bb_middle,  # Target mean reversion
                    stop_loss=current_price * 0.95,  # 5% stop loss
                    reasoning=f"Oversold: Price {current_price:.2f} < BB Lower {bb_lower:.2f}, RSI={rsi:.1f}"
                ))

            # Sell signal: price above upper BB + RSI overbought
            elif current_price > bb_upper and rsi > self.rsi_overbought:
                signals.append(TradingSignal(
                    symbol=symbol,
                    action="SELL",
                    confidence=self._calculate_reversion_confidence(
                        current_price, bb_middle, bb_upper, rsi, "SELL"
                    ),
                    entry_price=current_price,
                    take_profit=bb_middle,  # Target mean reversion
                    stop_loss=current_price * 1.05,  # 5% stop loss
                    reasoning=f"Overbought: Price {current_price:.2f} > BB Upper {bb_upper:.2f}, RSI={rsi:.1f}"
                ))

        return signals

    def _calculate_bollinger_bands(
        self,
        data: pd.DataFrame
    ) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands (upper, middle, lower)"""

        if len(data) < self.bollinger_period:
            return 0, 0, 0

        prices = data["close"]
        middle = prices.rolling(window=self.bollinger_period).mean()
        std = prices.rolling(window=self.bollinger_period).std()

        upper = middle + (std * self.bollinger_std)
        lower = middle - (std * self.bollinger_std)

        return upper.iloc[-1], middle.iloc[-1], lower.iloc[-1]

    def _calculate_reversion_confidence(
        self,
        current_price: float,
        mean_price: float,
        band_price: float,
        rsi: float,
        side: str
    ) -> float:
        """Calculate confidence in mean reversion"""

        # Distance from mean (normalized)
        if side == "BUY":
            distance_pct = (mean_price - current_price) / mean_price
            rsi_score = (self.rsi_oversold - rsi) / self.rsi_oversold
        else:  # SELL
            distance_pct = (current_price - mean_price) / mean_price
            rsi_score = (rsi - self.rsi_overbought) / (100 - self.rsi_overbought)

        # Combine distance and RSI for confidence
        confidence = (distance_pct * 0.6 + rsi_score * 0.4)
        return max(0, min(1, confidence))
```

### Crypto-Specific Considerations

**Volatility Regime Filter:** Only trade mean reversion in range-bound markets
```python
def is_ranging_market(data: pd.DataFrame, lookback: int = 30) -> bool:
    """Detect if market is range-bound vs trending"""
    returns = data["close"].pct_change()
    volatility = returns.rolling(lookback).std()

    # Calculate trend strength using ADX
    adx = calculate_adx(data)

    # Range-bound: low ADX + moderate volatility
    return adx < 25 and 0.01 < volatility.iloc[-1] < 0.05
```

**Avoid Catching Falling Knives:** Don't buy assets in structural decline
```python
def has_structural_support(data: pd.DataFrame) -> bool:
    """Check if asset has support levels"""
    # Ensure price above 200-day MA
    ma_200 = data["close"].rolling(200).mean()
    current_price = data["close"].iloc[-1]

    return current_price > ma_200.iloc[-1] * 0.9  # Within 10% of 200 MA
```

**Flash Crash Detection:** Avoid mean reversion during flash crashes
```python
def is_flash_crash(data: pd.DataFrame) -> bool:
    """Detect flash crashes (>10% drop in <5 minutes)"""
    recent_data = data.tail(5)  # Last 5 minutes
    drop_pct = (
        (recent_data["close"].max() - recent_data["close"].min())
        / recent_data["close"].max()
    )
    return drop_pct > 0.10
```

### Performance Metrics

**Key Metrics:**
- **Win Rate:** 60-75% (most reversions work)
- **Profit per Trade:** 2-8% (small consistent wins)
- **Trade Frequency:** 10-30 per week
- **Sharpe Ratio:** 1.5-3.0 (good risk-adjusted returns)
- **Max Drawdown:** 10-25% (moderate risk)

## 5. Grid Trading Strategy

### Concept

Place buy and sell orders at regular price intervals (grid levels). Profit from range-bound price oscillations without predicting direction.

### Algorithm

```python
class GridTradingStrategy:
    """Grid trading strategy for range-bound markets"""

    def __init__(
        self,
        symbol: str,
        grid_lower_bound: float,
        grid_upper_bound: float,
        num_grids: int = 10,
        order_size_per_grid: float = 100,  # USD per grid
        rebalance_threshold_pct: float = 0.10  # Rebalance if price moves 10% outside range
    ):
        self.symbol = symbol
        self.grid_lower_bound = grid_lower_bound
        self.grid_upper_bound = grid_upper_bound
        self.num_grids = num_grids
        self.order_size_per_grid = order_size_per_grid
        self.rebalance_threshold_pct = rebalance_threshold_pct

        self.grid_levels = self._calculate_grid_levels()
        self.active_orders = {}
        self.filled_orders = []

    def _calculate_grid_levels(self) -> List[float]:
        """Calculate price levels for grid"""

        price_range = self.grid_upper_bound - self.grid_lower_bound
        step = price_range / self.num_grids

        return [
            self.grid_lower_bound + (i * step)
            for i in range(self.num_grids + 1)
        ]

    async def initialize_grid(self, exchange: ExchangeAdapter):
        """Place initial grid orders"""

        current_price = await self._get_current_price(exchange)

        for i, price in enumerate(self.grid_levels):
            # Place buy orders below current price
            if price < current_price:
                order = await exchange.place_order(
                    symbol=self.symbol,
                    side="BUY",
                    order_type="LIMIT",
                    quantity=self.order_size_per_grid / price,
                    price=price,
                    time_in_force="GTC"
                )
                self.active_orders[order.order_id] = {
                    "order": order,
                    "grid_level": i,
                    "side": "BUY"
                }

            # Place sell orders above current price
            elif price > current_price:
                order = await exchange.place_order(
                    symbol=self.symbol,
                    side="SELL",
                    order_type="LIMIT",
                    quantity=self.order_size_per_grid / price,
                    price=price,
                    time_in_force="GTC"
                )
                self.active_orders[order.order_id] = {
                    "order": order,
                    "grid_level": i,
                    "side": "SELL"
                }

    async def handle_fill(self, filled_order: Order, exchange: ExchangeAdapter):
        """Handle filled order and place counter order"""

        order_info = self.active_orders.pop(filled_order.order_id)
        grid_level = order_info["grid_level"]
        side = order_info["side"]

        self.filled_orders.append(filled_order)

        # Place counter order at next grid level
        if side == "BUY":
            # Buy filled, place sell at next higher grid
            if grid_level + 1 < len(self.grid_levels):
                sell_price = self.grid_levels[grid_level + 1]
                sell_order = await exchange.place_order(
                    symbol=self.symbol,
                    side="SELL",
                    order_type="LIMIT",
                    quantity=filled_order.executed_qty,
                    price=sell_price,
                    time_in_force="GTC"
                )
                self.active_orders[sell_order.order_id] = {
                    "order": sell_order,
                    "grid_level": grid_level + 1,
                    "side": "SELL"
                }

        elif side == "SELL":
            # Sell filled, place buy at next lower grid
            if grid_level - 1 >= 0:
                buy_price = self.grid_levels[grid_level - 1]
                buy_order = await exchange.place_order(
                    symbol=self.symbol,
                    side="BUY",
                    order_type="LIMIT",
                    quantity=filled_order.executed_qty,
                    price=buy_price,
                    time_in_force="GTC"
                )
                self.active_orders[buy_order.order_id] = {
                    "order": buy_order,
                    "grid_level": grid_level - 1,
                    "side": "BUY"
                }

    async def check_rebalance(self, exchange: ExchangeAdapter):
        """Check if grid needs rebalancing"""

        current_price = await self._get_current_price(exchange)

        # Check if price moved outside grid range
        if (current_price < self.grid_lower_bound * (1 - self.rebalance_threshold_pct) or
            current_price > self.grid_upper_bound * (1 + self.rebalance_threshold_pct)):

            logger.info(f"Price {current_price} outside grid range, rebalancing...")

            # Cancel all orders
            await self._cancel_all_orders(exchange)

            # Recalculate grid bounds based on current price
            self.grid_lower_bound = current_price * 0.90  # -10%
            self.grid_upper_bound = current_price * 1.10  # +10%
            self.grid_levels = self._calculate_grid_levels()

            # Reinitialize grid
            await self.initialize_grid(exchange)

    def calculate_profit(self) -> float:
        """Calculate total profit from filled order pairs"""

        profit = 0

        # Match buy and sell pairs
        buys = [o for o in self.filled_orders if o.side == "BUY"]
        sells = [o for o in self.filled_orders if o.side == "SELL"]

        for buy, sell in zip(buys, sells):
            buy_cost = buy.price * buy.executed_qty
            sell_revenue = sell.price * sell.executed_qty
            profit += sell_revenue - buy_cost

        return profit
```

### Crypto-Specific Considerations

**Volatility-Adjusted Grid Spacing:** Wider grids for volatile assets
```python
def calculate_grid_spacing(volatility: float) -> float:
    """Adjust grid spacing based on volatility"""
    # Base spacing: 1%
    # High volatility (5% daily): 2.5% spacing
    return 0.01 * (1 + volatility / 0.02)
```

**Trending Market Detection:** Pause grid trading during strong trends
```python
async def should_pause_grid(data: pd.DataFrame) -> bool:
    """Pause grid if strong trend detected"""
    adx = calculate_adx(data)
    return adx > 30  # Strong trend
```

**Dynamic Grid Adjustment:** Adjust grid range as price moves
```python
async def dynamic_grid_adjustment(
    strategy: GridTradingStrategy,
    current_price: float
):
    """Adjust grid to follow price"""
    if current_price > strategy.grid_upper_bound:
        # Price broke above, shift grid up
        shift = current_price - strategy.grid_upper_bound
        strategy.grid_lower_bound += shift
        strategy.grid_upper_bound += shift
        await strategy.rebalance()
```

### Performance Metrics

**Key Metrics:**
- **Win Rate:** 70-85% (most oscillations profitable)
- **Profit per Trade:** 0.5-2% per grid level
- **Trade Frequency:** 20-100 per week (high activity)
- **Sharpe Ratio:** 1.0-2.5 (consistent returns in ranging markets)
- **Max Drawdown:** 15-30% (exposure during breakouts)

## Integration with crypto-agent-architect

All strategies integrate with crypto-agent-architect Layer 3 (Trading Strategy):

```python
from crypto_agent_architect import TradingStrategyLayer, RiskManager

# Create strategy instance
momentum_strategy = MomentumStrategy(
    lookback_periods=[7, 14, 30],
    min_momentum_score=0.7
)

# Integrate with Layer 3
strategy_layer = TradingStrategyLayer(
    strategies=[momentum_strategy],
    risk_manager=RiskManager(config=risk_config),
    position_sizer=PositionSizer()
)

# Strategy generates signals → Risk Manager validates → Orders executed
signals = await momentum_strategy.generate_signals(market_data)
validated_signals = await strategy_layer.risk_manager.validate(signals)
orders = await strategy_layer.execute_signals(validated_signals)
```

## Backtesting Framework

```bash
# Run backtesting engine
python scripts/backtest_engine.py \
  --strategy momentum \
  --symbols BTC/USDT,ETH/USDT \
  --start-date 2023-01-01 \
  --end-date 2024-01-01 \
  --initial-capital 100000 \
  --output results/momentum_backtest.json

# Optimize strategy parameters
python scripts/strategy_optimizer.py \
  --strategy mean-reversion \
  --optimize-params bollinger_std,rsi_oversold \
  --data historical_data/ \
  --metric sharpe_ratio
```

## Resources

### scripts/

- **backtest_engine.py** - Comprehensive backtesting framework with performance analytics
- **strategy_optimizer.py** - Grid search and Bayesian optimization for strategy parameters
- **risk_calculator.py** - Calculate position sizes, stop losses, risk metrics

### references/

- **strategy_comparison.md** - Detailed comparison of all 5 strategies with performance benchmarks
- **backtesting_guide.md** - Best practices for backtesting crypto strategies
- **crypto_market_microstructure.md** - Understanding liquidity, slippage, and order book dynamics

## Production Checklist

Before deploying strategies to production:

- [ ] **Backtesting:** ≥1 year historical data, Sharpe ratio >1.0, max drawdown <30%
- [ ] **Risk Controls:** Position sizing, stop losses, max drawdown limits implemented
- [ ] **Crypto Optimizations:** Gas fee checks (DEX), slippage limits, MEV protection
- [ ] **Paper Trading:** ≥30 days paper trading with live data, positive P&L
- [ ] **Monitoring:** Real-time P&L tracking, alert on consecutive losses (≥3)
- [ ] **Kill Switch:** Emergency stop at -15% drawdown or circuit breaker trigger
- [ ] **Testing:** ≥80% test coverage, integration tests with mock exchanges
- [ ] **Documentation:** Strategy logic, parameters, expected performance documented
- [ ] **Compliance:** Trading limits, audit trail, regulatory compliance checks
- [ ] **Integration:** Properly integrated with crypto-agent-architect layers

## Support

For implementation guidance:
- Reference strategy comparison in `references/strategy_comparison.md`
- Run backtests with `scripts/backtest_engine.py`
- Optimize parameters with `scripts/strategy_optimizer.py`
- Integrate with crypto-agent-architect Layer 3 for production deployment
