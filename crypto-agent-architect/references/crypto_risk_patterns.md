# Crypto-Specific Risk Management Patterns

Comprehensive guide to crypto-specific risk management for trading agents.

## Overview

Crypto markets have unique risk characteristics that differ from traditional finance:

- **24/7 Trading:** No market close, risks can materialize anytime
- **High Volatility:** 10-20% daily swings are common
- **Low Liquidity:** Small cap coins can have wide bid-ask spreads
- **Flash Crashes:** Rapid price drops due to liquidation cascades
- **MEV (Maximal Extractable Value):** Front-running and sandwich attacks on DEX
- **Gas Fees:** Transaction costs can exceed profit on small trades
- **Slippage:** Larger than expected due to thin order books

## Position Sizing

### Kelly Criterion with Crypto Adjustments

Traditional Kelly Criterion:

```
f* = (p × b - q) / b
```

Where:
- `f*` = fraction of bankroll to bet
- `p` = win probability
- `q` = loss probability (1 - p)
- `b` = win/loss ratio (avg win / avg loss)

**Crypto Adjustments:**

1. **Use Fractional Kelly (0.25):** Full Kelly too aggressive for crypto volatility
2. **Volatility Discount:** Reduce position size during high volatility
3. **Liquidity Adjustment:** Reduce size for low liquidity pairs

```python
class CryptoPositionSizer:
    """Position sizing with crypto-specific adjustments."""

    def calculate_position_size(
        self,
        portfolio_value: float,
        win_rate: float,
        win_loss_ratio: float,
        volatility: float,  # 30-day volatility
        liquidity_score: float,  # 0-1, based on volume
        signal_strength: float  # 0-1, from strategy
    ) -> float:
        """Calculate position size with crypto adjustments."""

        # Standard Kelly
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio

        # Fractional Kelly (0.25 = quarter Kelly)
        kelly_fraction = 0.25
        position_pct = kelly * kelly_fraction

        # Volatility discount (reduce size if vol > 50%)
        if volatility > 0.50:
            vol_discount = max(0.5, 1 - (volatility - 0.50))
            position_pct *= vol_discount

        # Liquidity adjustment (reduce if liquidity < 0.7)
        if liquidity_score < 0.7:
            position_pct *= liquidity_score

        # Signal strength scaling
        position_pct *= signal_strength

        # Cap at 5% per position
        position_pct = min(position_pct, 0.05)

        return portfolio_value * position_pct
```

### Volatility-Based Sizing

Adjust position size based on realized volatility:

```python
def volatility_adjusted_size(
    base_size: float,
    current_vol: float,
    target_vol: float = 0.30  # 30% annualized
) -> float:
    """Scale position size inverse to volatility."""

    # If volatility 2x target, use half position size
    size_multiplier = target_vol / current_vol

    # Cap multiplier between 0.25 and 2.0
    size_multiplier = max(0.25, min(2.0, size_multiplier))

    return base_size * size_multiplier
```

## Liquidation Risk Management

### Liquidation Price Calculation

For leveraged positions, calculate liquidation price:

```python
def calculate_liquidation_price(
    entry_price: float,
    leverage: float,
    side: str,  # "LONG" or "SHORT"
    maintenance_margin: float = 0.005  # 0.5%
) -> float:
    """Calculate liquidation price for leveraged position."""

    if side == "LONG":
        # Long liquidation: entry * (1 - 1/leverage + maintenance_margin)
        liq_price = entry_price * (1 - 1/leverage + maintenance_margin)
    else:
        # Short liquidation: entry * (1 + 1/leverage - maintenance_margin)
        liq_price = entry_price * (1 + 1/leverage - maintenance_margin)

    return liq_price
```

### Liquidation Buffer

Maintain buffer above liquidation price:

```python
class LiquidationRiskManager:
    """Manage liquidation risk for leveraged positions."""

    def __init__(self, min_buffer: float = 0.20):
        self.min_buffer = min_buffer  # 20% buffer

    def validate_position(
        self,
        entry_price: float,
        current_price: float,
        leverage: float,
        side: str
    ) -> bool:
        """Validate position has sufficient buffer from liquidation."""

        liq_price = calculate_liquidation_price(entry_price, leverage, side)

        if side == "LONG":
            # For long, liquidation below current price
            buffer = (current_price - liq_price) / current_price
        else:
            # For short, liquidation above current price
            buffer = (liq_price - current_price) / current_price

        return buffer >= self.min_buffer

    def calculate_safe_leverage(
        self,
        expected_drawdown: float = 0.10,  # Expect 10% drawdown
        buffer: float = 0.20  # Want 20% buffer
    ) -> float:
        """Calculate maximum safe leverage."""

        # Max leverage = 1 / (expected_drawdown + buffer)
        max_leverage = 1 / (expected_drawdown + buffer)

        return max_leverage
```

## Gas Fee Optimization (DeFi)

### Gas-Aware Trading

For DeFi trading, gas fees can exceed profit:

```python
class GasAwareTradeValidator:
    """Validate trades are profitable after gas costs."""

    def __init__(self, min_profit_ratio: float = 2.0):
        self.min_profit_ratio = min_profit_ratio  # Profit must be 2x gas cost

    def validate_trade(
        self,
        expected_profit: float,
        gas_price_gwei: float,
        gas_limit: int = 150000  # Typical swap gas limit
    ) -> bool:
        """Validate trade is profitable after gas."""

        # Calculate gas cost in USD
        eth_price = self.get_eth_price()
        gas_cost_eth = (gas_price_gwei * gas_limit) / 1e9
        gas_cost_usd = gas_cost_eth * eth_price

        # Profit must exceed gas cost by ratio
        return expected_profit >= gas_cost_usd * self.min_profit_ratio

    def calculate_min_trade_size(
        self,
        gas_price_gwei: float,
        profit_margin: float = 0.01,  # 1% expected profit
        gas_limit: int = 150000
    ) -> float:
        """Calculate minimum trade size to be profitable."""

        eth_price = self.get_eth_price()
        gas_cost_usd = (gas_price_gwei * gas_limit / 1e9) * eth_price

        # Trade size must be: gas_cost * ratio / profit_margin
        min_size = (gas_cost_usd * self.min_profit_ratio) / profit_margin

        return min_size
```

### Gas Price Monitoring

Monitor gas prices and delay trades during high gas:

```python
class GasPriceMonitor:
    """Monitor Ethereum gas prices."""

    def __init__(self, max_gas_gwei: float = 50):
        self.max_gas_gwei = max_gas_gwei

    async def get_current_gas_price(self) -> float:
        """Get current gas price in gwei."""
        # Use etherscan or web3 to get gas price
        pass

    async def should_execute_trade(self) -> bool:
        """Check if gas price is acceptable."""

        current_gas = await self.get_current_gas_price()

        if current_gas > self.max_gas_gwei:
            logger.warning(
                f"Gas price {current_gas} gwei exceeds limit {self.max_gas_gwei}"
            )
            return False

        return True
```

## MEV Protection (DeFi)

### MEV Attack Vectors

1. **Front-running:** Attacker sees your trade, submits same trade with higher gas
2. **Sandwich Attack:** Attacker front-runs and back-runs your trade
3. **Liquidation:** Attacker monitors positions, liquidates before you can

### Protection Strategies

```python
class MEVProtection:
    """Protect against MEV attacks."""

    def __init__(self):
        self.flashbots_rpc = "https://rpc.flashbots.net"

    def use_flashbots(self, transaction) -> bool:
        """Send transaction via Flashbots private mempool."""

        # Flashbots prevents front-running by keeping tx private
        # until included in block
        pass

    def set_slippage_protection(
        self,
        expected_price: float,
        max_slippage: float = 0.01  # 1%
    ) -> tuple[float, float]:
        """Set min/max prices for trade."""

        min_price = expected_price * (1 - max_slippage)
        max_price = expected_price * (1 + max_slippage)

        return min_price, max_price

    def validate_trade_execution(
        self,
        expected_price: float,
        executed_price: float,
        max_slippage: float = 0.01
    ) -> bool:
        """Validate execution price within acceptable slippage."""

        actual_slippage = abs(executed_price - expected_price) / expected_price

        if actual_slippage > max_slippage:
            logger.warning(
                f"Slippage {actual_slippage:.2%} exceeded limit {max_slippage:.2%}"
            )
            return False

        return True
```

## Flash Crash Protection

### Circuit Breakers

Halt trading during extreme price movements:

```python
class CircuitBreaker:
    """Circuit breaker for flash crashes."""

    def __init__(
        self,
        price_drop_threshold: float = 0.20,  # 20% drop
        time_window: int = 300  # 5 minutes
    ):
        self.price_drop_threshold = price_drop_threshold
        self.time_window = time_window
        self.price_history = []

    def check_flash_crash(self, current_price: float) -> bool:
        """Detect potential flash crash."""

        now = time.time()

        # Add current price
        self.price_history.append((now, current_price))

        # Remove old prices
        self.price_history = [
            (t, p) for t, p in self.price_history
            if now - t < self.time_window
        ]

        if len(self.price_history) < 2:
            return False

        # Check for rapid price drop
        max_price = max(p for _, p in self.price_history)
        price_drop = (max_price - current_price) / max_price

        if price_drop >= self.price_drop_threshold:
            logger.critical(
                f"Flash crash detected: {price_drop:.2%} drop in {self.time_window}s"
            )
            return True

        return False

    def halt_trading(self):
        """Halt all trading activity."""
        logger.critical("Trading halted due to circuit breaker")
        # Close all positions at market
        # Stop accepting new orders
```

### Volatility Filters

Filter trades during high volatility:

```python
class VolatilityFilter:
    """Filter trades during extreme volatility."""

    def __init__(self, max_volatility: float = 0.50):
        self.max_volatility = max_volatility  # 50% daily volatility

    def calculate_volatility(self, price_history: list[float]) -> float:
        """Calculate realized volatility."""

        returns = [
            (price_history[i] - price_history[i-1]) / price_history[i-1]
            for i in range(1, len(price_history))
        ]

        # Annualized volatility
        std_dev = np.std(returns)
        volatility = std_dev * np.sqrt(365)

        return volatility

    def should_allow_trade(self, volatility: float) -> bool:
        """Check if volatility is acceptable."""

        if volatility > self.max_volatility:
            logger.warning(
                f"Volatility {volatility:.2%} exceeds limit {self.max_volatility:.2%}"
            )
            return False

        return True
```

## Slippage Management

### Slippage Estimation

Estimate slippage before trade:

```python
class SlippageEstimator:
    """Estimate slippage for trades."""

    def estimate_slippage(
        self,
        order_size: float,
        orderbook: dict,
        side: str  # "BUY" or "SELL"
    ) -> float:
        """Estimate slippage based on order book depth."""

        levels = orderbook['asks'] if side == "BUY" else orderbook['bids']

        total_filled = 0
        weighted_price = 0

        for price, quantity in levels:
            if total_filled >= order_size:
                break

            fill_qty = min(quantity, order_size - total_filled)
            weighted_price += price * fill_qty
            total_filled += fill_qty

        if total_filled == 0:
            return float('inf')  # Insufficient liquidity

        avg_execution_price = weighted_price / total_filled
        current_price = float(levels[0][0])

        slippage = abs(avg_execution_price - current_price) / current_price

        return slippage
```

### Dynamic Slippage Limits

Adjust slippage tolerance based on market conditions:

```python
class DynamicSlippageManager:
    """Manage slippage dynamically."""

    def calculate_max_slippage(
        self,
        base_slippage: float = 0.005,  # 0.5%
        volatility: float = 0.30,
        liquidity_score: float = 0.8
    ) -> float:
        """Calculate acceptable slippage."""

        # Higher slippage during high volatility
        vol_multiplier = 1 + (volatility - 0.30)  # Base vol = 30%

        # Higher slippage for low liquidity
        liq_multiplier = 2 - liquidity_score  # 1.2x for 0.8 liquidity

        max_slippage = base_slippage * vol_multiplier * liq_multiplier

        # Cap at 2%
        return min(max_slippage, 0.02)
```

## Correlation Risk

### Portfolio Correlation

Avoid excessive correlation in portfolio:

```python
class CorrelationRiskManager:
    """Manage correlation risk in portfolio."""

    def __init__(self, max_correlation: float = 0.70):
        self.max_correlation = max_correlation

    def calculate_portfolio_correlation(
        self,
        positions: list[str],
        price_history: dict[str, list[float]]
    ) -> float:
        """Calculate average portfolio correlation."""

        correlations = []

        for i, asset1 in enumerate(positions):
            for asset2 in positions[i+1:]:
                corr = np.corrcoef(
                    price_history[asset1],
                    price_history[asset2]
                )[0, 1]

                correlations.append(abs(corr))

        return np.mean(correlations) if correlations else 0

    def validate_new_position(
        self,
        new_asset: str,
        existing_positions: list[str],
        price_history: dict
    ) -> bool:
        """Validate new position doesn't increase correlation too much."""

        if not existing_positions:
            return True

        # Calculate correlation with existing positions
        correlations = [
            abs(np.corrcoef(
                price_history[new_asset],
                price_history[existing]
            )[0, 1])
            for existing in existing_positions
        ]

        avg_correlation = np.mean(correlations)

        if avg_correlation > self.max_correlation:
            logger.warning(
                f"New position correlation {avg_correlation:.2f} exceeds limit"
            )
            return False

        return True
```

## Drawdown Management

### Maximum Drawdown Limits

Implement kill switch for excessive drawdown:

```python
class DrawdownManager:
    """Manage portfolio drawdown."""

    def __init__(self, max_drawdown: float = 0.15):
        self.max_drawdown = max_drawdown  # 15% max drawdown
        self.peak_value = 0
        self.kill_switch_activated = False

    def update(self, current_value: float):
        """Update peak and check drawdown."""

        # Update peak
        if current_value > self.peak_value:
            self.peak_value = current_value

        # Calculate current drawdown
        drawdown = (self.peak_value - current_value) / self.peak_value

        if drawdown >= self.max_drawdown:
            self.activate_kill_switch(drawdown)

        return drawdown

    def activate_kill_switch(self, drawdown: float):
        """Activate kill switch - stop all trading."""

        if self.kill_switch_activated:
            return

        self.kill_switch_activated = True

        logger.critical(
            f"KILL SWITCH ACTIVATED: Drawdown {drawdown:.2%} exceeded limit {self.max_drawdown:.2%}"
        )

        # Close all positions
        # Stop accepting new trades
        # Alert all channels
```

## Testing Risk Management

### Stress Testing

Test risk management under extreme conditions:

```python
@pytest.mark.parametrize("volatility", [0.50, 1.0, 2.0])
@pytest.mark.parametrize("drawdown", [0.10, 0.20, 0.30])
def test_risk_management_under_stress(volatility, drawdown):
    """Test risk management holds under stress."""

    risk_manager = RiskManager(max_drawdown=0.15)

    # Simulate extreme conditions
    portfolio = simulate_portfolio(
        volatility=volatility,
        max_drawdown=drawdown
    )

    # Risk manager should halt trading
    if drawdown > risk_manager.max_drawdown:
        assert risk_manager.kill_switch_activated

    # Position sizing should decrease with volatility
    position_size = risk_manager.calculate_position_size(
        volatility=volatility
    )

    assert position_size < risk_manager.base_position_size
```

## Best Practices

1. **Always use stop-losses** - Set stop-loss 2-5% below entry
2. **Never risk >2% per trade** - Limit position size to 2% of portfolio
3. **Monitor liquidation risk** - Keep 20%+ buffer from liquidation price
4. **Account for gas fees** - DeFi trades must be 2x+ gas cost to be profitable
5. **Use Flashbots for large trades** - Prevent MEV attacks
6. **Set circuit breakers** - Halt trading on >20% price drops in 5 minutes
7. **Diversify across uncorrelated assets** - Keep portfolio correlation <70%
8. **Implement kill switch** - Auto-halt trading at 15% drawdown
9. **Test extensively on Testnet** - Validate all risk controls before live trading
10. **Monitor 24/7** - Crypto markets never sleep, neither should monitoring

## Resources

- **Position Sizing:** https://www.quantifiedstrategies.com/kelly-criterion/
- **MEV Protection:** https://docs.flashbots.net/
- **Gas Optimization:** https://www.evm.codes/
- **Risk Management:** https://www.investopedia.com/articles/trading/09/risk-management.asp
