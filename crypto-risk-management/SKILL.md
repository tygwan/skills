---
name: crypto-risk-management
description: Comprehensive crypto trading risk management covering position sizing (Kelly Criterion), liquidation monitoring, gas optimization, slippage control, MEV protection, and drawdown limits. Use for crypto trading bots, DeFi protocols, and automated strategies requiring robust risk controls. Integrates with crypto-agent-architect Risk Manager.
---

# Crypto Risk Management

## Overview

Implement production-grade risk management for cryptocurrency trading systems. This skill provides comprehensive frameworks for detecting, mitigating, and monitoring six critical risk types specific to crypto markets: position sizing, liquidation risk, gas costs, slippage, MEV attacks, and portfolio drawdown.

**Use this skill when:**
- Building automated crypto trading bots with risk controls
- Implementing DeFi protocols requiring liquidation monitoring
- Optimizing gas costs for high-frequency on-chain strategies
- Protecting against slippage and MEV attacks in DEX trading
- Managing portfolio risk with Kelly Criterion position sizing
- Integrating risk management into crypto-agent-architect systems

## Core Risk Types

### Risk Priority Matrix

| Risk Type | Severity | Frequency | Detection Time | Mitigation Cost |
|-----------|----------|-----------|----------------|-----------------|
| Liquidation | Critical | Low | Real-time | High |
| Drawdown | High | Medium | Daily | Medium |
| Slippage | Medium | High | Per-trade | Low |
| Gas Costs | Medium | High | Pre-tx | Low |
| MEV | Medium | Medium | Post-tx | Medium |
| Position Sizing | High | Per-trade | Pre-trade | None |

## 1. Position Sizing (Kelly Criterion)

**Purpose:** Calculate optimal position sizes to maximize long-term growth while controlling risk.

### Kelly Criterion Formula

```
Kelly % = (Win Rate × Avg Win) - (Loss Rate × Avg Loss) / Avg Win
Fractional Kelly = Kelly % × 0.25  # Conservative: use 1/4 Kelly
```

### Implementation

**Position Size Calculator:**

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class TradingMetrics:
    """Historical trading performance metrics"""
    total_trades: int
    wins: int
    losses: int
    avg_win: float  # Average winning trade return (e.g., 0.05 = 5%)
    avg_loss: float  # Average losing trade return (e.g., -0.03 = -3%)
    portfolio_value: float
    max_position_pct: float = 0.10  # Max 10% per position

class KellyPositionSizer:
    """Calculate optimal position sizes using Kelly Criterion"""

    def __init__(self, metrics: TradingMetrics, fractional_kelly: float = 0.25):
        self.metrics = metrics
        self.fractional_kelly = fractional_kelly

    def calculate_kelly_pct(self) -> float:
        """Calculate raw Kelly percentage"""
        win_rate = self.metrics.wins / self.metrics.total_trades
        loss_rate = self.metrics.losses / self.metrics.total_trades

        if self.metrics.avg_win == 0:
            return 0.0

        kelly_pct = (
            (win_rate * self.metrics.avg_win) -
            (loss_rate * abs(self.metrics.avg_loss))
        ) / self.metrics.avg_win

        return max(0.0, kelly_pct)  # Never negative

    def get_position_size(
        self,
        signal_confidence: float = 1.0
    ) -> dict:
        """Get recommended position size in USD and percentage"""
        raw_kelly = self.calculate_kelly_pct()
        adjusted_kelly = raw_kelly * self.fractional_kelly * signal_confidence

        # Apply maximum position size limit
        final_pct = min(adjusted_kelly, self.metrics.max_position_pct)

        position_usd = self.metrics.portfolio_value * final_pct

        return {
            "raw_kelly_pct": raw_kelly,
            "fractional_kelly_pct": adjusted_kelly,
            "final_position_pct": final_pct,
            "position_usd": position_usd,
            "max_loss_usd": position_usd * abs(self.metrics.avg_loss),
            "confidence_adjusted": signal_confidence < 1.0
        }

# Usage Example
metrics = TradingMetrics(
    total_trades=100,
    wins=60,
    losses=40,
    avg_win=0.08,  # 8% average win
    avg_loss=-0.05,  # 5% average loss
    portfolio_value=100000.0
)

sizer = KellyPositionSizer(metrics, fractional_kelly=0.25)

# High confidence signal (90%)
position = sizer.get_position_size(signal_confidence=0.9)
# Result: ~$2,700 position (2.7% of portfolio)

# Low confidence signal (50%)
position_low = sizer.get_position_size(signal_confidence=0.5)
# Result: ~$1,500 position (1.5% of portfolio)
```

### Risk Controls

**Position Size Limits:**
- **Max Single Position:** 10% of portfolio (hard limit)
- **Max Total Exposure:** 50% of portfolio across all positions
- **Min Position Size:** $100 or 0.1% of portfolio (avoid dust trades)
- **Confidence Scaling:** Reduce size for lower confidence signals

**Kelly Criterion Best Practices:**
- Use fractional Kelly (0.25-0.5) to reduce volatility
- Recalculate metrics every 50-100 trades
- Account for correlation between positions
- Never use full Kelly in live trading (too aggressive)

## 2. Liquidation Risk Monitoring

**Purpose:** Prevent forced liquidation on leveraged positions through real-time monitoring and automated risk reduction.

### Liquidation Price Calculation

**For Long Positions:**
```
Liquidation Price = Entry Price × (1 - Initial Margin / Leverage)
```

**For Short Positions:**
```
Liquidation Price = Entry Price × (1 + Initial Margin / Leverage)
```

### Implementation

**Liquidation Monitor:**

```python
from enum import Enum
from datetime import datetime

class LiquidationRisk(Enum):
    SAFE = "safe"  # >20% from liquidation
    WARNING = "warning"  # 10-20% from liquidation
    DANGER = "danger"  # 5-10% from liquidation
    CRITICAL = "critical"  # <5% from liquidation

@dataclass
class LeveragedPosition:
    symbol: str
    side: str  # "LONG" or "SHORT"
    entry_price: float
    position_size: float  # in base asset
    leverage: float
    initial_margin: float
    maintenance_margin_rate: float = 0.005  # 0.5% for most exchanges

class LiquidationMonitor:
    """Monitor and manage liquidation risk"""

    def __init__(self, position: LeveragedPosition):
        self.position = position

    def calculate_liquidation_price(self) -> float:
        """Calculate exact liquidation price"""
        margin_ratio = self.position.initial_margin / self.position.leverage

        if self.position.side == "LONG":
            return self.position.entry_price * (1 - margin_ratio)
        else:  # SHORT
            return self.position.entry_price * (1 + margin_ratio)

    def get_distance_to_liquidation(self, current_price: float) -> float:
        """Calculate percentage distance to liquidation"""
        liq_price = self.calculate_liquidation_price()

        if self.position.side == "LONG":
            distance_pct = ((current_price - liq_price) / current_price) * 100
        else:  # SHORT
            distance_pct = ((liq_price - current_price) / current_price) * 100

        return distance_pct

    def assess_risk(self, current_price: float) -> dict:
        """Assess current liquidation risk level"""
        liq_price = self.calculate_liquidation_price()
        distance_pct = self.get_distance_to_liquidation(current_price)

        if distance_pct < 5:
            risk = LiquidationRisk.CRITICAL
            action = "CLOSE_IMMEDIATELY"
        elif distance_pct < 10:
            risk = LiquidationRisk.DANGER
            action = "REDUCE_LEVERAGE"
        elif distance_pct < 20:
            risk = LiquidationRisk.WARNING
            action = "MONITOR_CLOSELY"
        else:
            risk = LiquidationRisk.SAFE
            action = "CONTINUE"

        return {
            "risk_level": risk.value,
            "liquidation_price": liq_price,
            "current_price": current_price,
            "distance_pct": distance_pct,
            "recommended_action": action,
            "timestamp": datetime.now().isoformat()
        }

# Usage Example
position = LeveragedPosition(
    symbol="BTCUSDT",
    side="LONG",
    entry_price=50000.0,
    position_size=1.0,  # 1 BTC
    leverage=10.0,
    initial_margin=5000.0  # $5,000 margin
)

monitor = LiquidationMonitor(position)
risk = monitor.assess_risk(current_price=48000.0)
# Result: WARNING - liquidation at $45,000, 6.25% away
```

### Automated Risk Reduction

**Liquidation Protection Strategy:**

1. **Safe Zone (>20%):** No action required
2. **Warning Zone (10-20%):** Add margin or reduce position by 25%
3. **Danger Zone (5-10%):** Reduce position by 50% immediately
4. **Critical Zone (<5%):** Close entire position at market

**Stop-Loss Integration:**
- Place stop-loss at 15% from liquidation price
- Use trailing stop-loss when in profit
- Never risk more than 2% of portfolio per trade

## 3. Gas Optimization (On-Chain Transactions)

**Purpose:** Minimize transaction costs for on-chain operations through intelligent gas estimation and batching.

### Gas Estimation Strategy

**Dynamic Gas Pricing:**

```python
from web3 import Web3
from typing import Optional

class GasOptimizer:
    """Optimize gas costs for Ethereum transactions"""

    def __init__(self, w3: Web3, network: str = "mainnet"):
        self.w3 = w3
        self.network = network
        self.base_gas_limit = {
            "simple_transfer": 21000,
            "erc20_transfer": 65000,
            "uniswap_swap": 150000,
            "complex_defi": 300000
        }

    def get_current_gas_prices(self) -> dict:
        """Get current gas prices in Gwei"""
        try:
            latest_block = self.w3.eth.get_block('latest')
            base_fee = latest_block.get('baseFeePerGas', 0)

            # Priority fees for different speeds
            priority_fees = {
                "slow": self.w3.to_wei(1, 'gwei'),     # ~5 min
                "medium": self.w3.to_wei(1.5, 'gwei'), # ~2 min
                "fast": self.w3.to_wei(2, 'gwei')      # ~30 sec
            }

            gas_prices = {}
            for speed, priority in priority_fees.items():
                max_fee = base_fee + priority
                gas_prices[speed] = {
                    "max_fee_per_gas": max_fee,
                    "max_priority_fee_per_gas": priority,
                    "max_fee_gwei": self.w3.from_wei(max_fee, 'gwei'),
                    "base_fee_gwei": self.w3.from_wei(base_fee, 'gwei')
                }

            return gas_prices

        except Exception as e:
            # Fallback to legacy gas price
            legacy_price = self.w3.eth.gas_price
            return {
                "legacy": {
                    "gas_price": legacy_price,
                    "gas_price_gwei": self.w3.from_wei(legacy_price, 'gwei')
                }
            }

    def estimate_transaction_cost(
        self,
        tx_type: str,
        speed: str = "medium",
        eth_price_usd: Optional[float] = None
    ) -> dict:
        """Estimate total transaction cost"""
        gas_prices = self.get_current_gas_prices()
        gas_limit = self.base_gas_limit.get(tx_type, 100000)

        if speed in gas_prices:
            max_fee = gas_prices[speed]["max_fee_per_gas"]
            max_cost_wei = gas_limit * max_fee
            max_cost_eth = self.w3.from_wei(max_cost_wei, 'ether')

            result = {
                "tx_type": tx_type,
                "gas_limit": gas_limit,
                "speed": speed,
                "max_fee_gwei": gas_prices[speed]["max_fee_gwei"],
                "max_cost_eth": float(max_cost_eth),
                "base_fee_gwei": gas_prices[speed]["base_fee_gwei"]
            }

            if eth_price_usd:
                result["max_cost_usd"] = float(max_cost_eth) * eth_price_usd

            return result

        else:  # Legacy pricing
            legacy_price = gas_prices["legacy"]["gas_price"]
            cost_wei = gas_limit * legacy_price
            cost_eth = self.w3.from_wei(cost_wei, 'ether')

            return {
                "tx_type": tx_type,
                "gas_limit": gas_limit,
                "gas_price_gwei": gas_prices["legacy"]["gas_price_gwei"],
                "cost_eth": float(cost_eth),
                "cost_usd": float(cost_eth) * eth_price_usd if eth_price_usd else None
            }

    def should_execute_transaction(
        self,
        tx_type: str,
        expected_profit_usd: float,
        eth_price_usd: float,
        min_profit_ratio: float = 2.0
    ) -> dict:
        """Determine if transaction is worth executing based on gas costs"""
        cost = self.estimate_transaction_cost(tx_type, "medium", eth_price_usd)
        gas_cost_usd = cost.get("max_cost_usd") or cost.get("cost_usd", 0)

        net_profit = expected_profit_usd - gas_cost_usd
        profit_ratio = expected_profit_usd / gas_cost_usd if gas_cost_usd > 0 else float('inf')

        should_execute = profit_ratio >= min_profit_ratio

        return {
            "should_execute": should_execute,
            "expected_profit_usd": expected_profit_usd,
            "gas_cost_usd": gas_cost_usd,
            "net_profit_usd": net_profit,
            "profit_ratio": profit_ratio,
            "min_profit_ratio": min_profit_ratio,
            "reason": "Profitable" if should_execute else "Gas costs too high"
        }

# Usage Example
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_KEY'))
optimizer = GasOptimizer(w3)

# Check if arbitrage opportunity is worth taking
decision = optimizer.should_execute_transaction(
    tx_type="uniswap_swap",
    expected_profit_usd=50.0,
    eth_price_usd=3000.0,
    min_profit_ratio=2.0
)
# Result: Execute if profit > 2x gas cost
```

### Gas Optimization Strategies

**Transaction Batching:**
- Combine multiple operations into single transaction
- Use multicall contracts (e.g., Multicall3)
- Batch token approvals with transfers

**Timing Optimization:**
- Monitor gas prices and execute during low-cost periods
- Weekend transactions typically 20-30% cheaper
- Avoid peak hours (9 AM - 5 PM EST)

**Contract Optimization:**
- Use gas-efficient contract patterns
- Minimize storage writes (most expensive operation)
- Cache frequently accessed data off-chain

## 4. Slippage Control

**Purpose:** Protect trades from excessive price movement between order placement and execution.

### Slippage Calculation

```python
from decimal import Decimal
from typing import Optional

class SlippageController:
    """Calculate and enforce slippage limits"""

    def __init__(self, max_slippage_pct: float = 0.5):
        self.max_slippage_pct = max_slippage_pct  # 0.5% default

    def calculate_slippage(
        self,
        expected_price: float,
        executed_price: float
    ) -> float:
        """Calculate actual slippage percentage"""
        slippage_pct = abs(
            (executed_price - expected_price) / expected_price
        ) * 100
        return slippage_pct

    def get_price_limits(
        self,
        side: str,
        market_price: float,
        slippage_tolerance_pct: Optional[float] = None
    ) -> dict:
        """Calculate min/max acceptable execution prices"""
        tolerance = slippage_tolerance_pct or self.max_slippage_pct
        tolerance_decimal = tolerance / 100

        if side == "BUY":
            max_price = market_price * (1 + tolerance_decimal)
            return {
                "side": "BUY",
                "market_price": market_price,
                "max_acceptable_price": max_price,
                "slippage_tolerance_pct": tolerance
            }
        else:  # SELL
            min_price = market_price * (1 - tolerance_decimal)
            return {
                "side": "SELL",
                "market_price": market_price,
                "min_acceptable_price": min_price,
                "slippage_tolerance_pct": tolerance
            }

    def estimate_dex_slippage(
        self,
        trade_size_usd: float,
        pool_liquidity_usd: float,
        pool_fee_pct: float = 0.3
    ) -> dict:
        """Estimate slippage for DEX trade"""
        # Simplified constant product formula impact
        size_ratio = trade_size_usd / pool_liquidity_usd
        price_impact_pct = (size_ratio / (1 - size_ratio)) * 100

        total_slippage = price_impact_pct + pool_fee_pct

        return {
            "trade_size_usd": trade_size_usd,
            "pool_liquidity_usd": pool_liquidity_usd,
            "price_impact_pct": price_impact_pct,
            "pool_fee_pct": pool_fee_pct,
            "total_slippage_pct": total_slippage,
            "acceptable": total_slippage <= self.max_slippage_pct
        }

# Usage Example
controller = SlippageController(max_slippage_pct=0.5)

# For CEX limit order
limits = controller.get_price_limits(
    side="BUY",
    market_price=50000.0,
    slippage_tolerance_pct=0.3
)
# Result: Max buy price = $50,150 (0.3% slippage)

# For DEX trade
slippage = controller.estimate_dex_slippage(
    trade_size_usd=10000.0,
    pool_liquidity_usd=1000000.0,
    pool_fee_pct=0.3
)
# Result: 1.3% total slippage (1% price impact + 0.3% fee)
```

### Slippage Mitigation

**CEX Strategies:**
- Use limit orders instead of market orders
- Split large orders into smaller chunks (TWAP/VWAP)
- Place orders during high liquidity periods

**DEX Strategies:**
- Route through multiple pools to reduce price impact
- Use aggregators (1inch, CowSwap) for optimal routing
- Avoid trading low-liquidity pairs

**Dynamic Slippage Adjustment:**
```python
def adjust_slippage_for_volatility(
    base_slippage_pct: float,
    current_volatility: float,
    normal_volatility: float = 0.02
) -> float:
    """Increase slippage tolerance during high volatility"""
    volatility_ratio = current_volatility / normal_volatility
    adjusted_slippage = base_slippage_pct * volatility_ratio
    return min(adjusted_slippage, 5.0)  # Cap at 5%
```

## 5. MEV Protection

**Purpose:** Protect transactions from front-running, sandwich attacks, and other MEV exploitation.

### MEV Attack Detection

```python
from dataclasses import dataclass
from typing import List

@dataclass
class Transaction:
    hash: str
    from_address: str
    to_address: str
    value: float
    gas_price: int
    block_number: int
    transaction_index: int

class MEVDetector:
    """Detect potential MEV attacks"""

    def detect_sandwich_attack(
        self,
        victim_tx: Transaction,
        surrounding_txs: List[Transaction]
    ) -> dict:
        """Detect if transaction was sandwiched"""
        same_block = [
            tx for tx in surrounding_txs
            if tx.block_number == victim_tx.block_number
        ]

        # Check for front-run (higher gas, before victim)
        front_run = [
            tx for tx in same_block
            if tx.transaction_index < victim_tx.transaction_index
            and tx.gas_price > victim_tx.gas_price
            and tx.to_address == victim_tx.to_address
        ]

        # Check for back-run (after victim)
        back_run = [
            tx for tx in same_block
            if tx.transaction_index > victim_tx.transaction_index
            and tx.to_address == victim_tx.to_address
        ]

        is_sandwich = len(front_run) > 0 and len(back_run) > 0

        return {
            "is_sandwich_attack": is_sandwich,
            "victim_tx": victim_tx.hash,
            "front_run_txs": [tx.hash for tx in front_run],
            "back_run_txs": [tx.hash for tx in back_run],
            "estimated_loss": self._estimate_sandwich_loss(
                victim_tx, front_run, back_run
            ) if is_sandwich else 0
        }

    def _estimate_sandwich_loss(
        self,
        victim_tx: Transaction,
        front_run: List[Transaction],
        back_run: List[Transaction]
    ) -> float:
        """Estimate loss from sandwich attack"""
        # Simplified: assume 1-5% loss based on attack sophistication
        if front_run and back_run:
            return victim_tx.value * 0.02  # Approximate 2% loss
        return 0.0
```

### MEV Protection Strategies

**Private Transaction Pools:**
- Use Flashbots Protect RPC for private mempool
- Submit transactions to MEV-resistant RPCs (bloXroute, Eden)
- Avoid public mempool for large trades

**Transaction Design:**
- Set minimal slippage tolerance
- Use deadline parameters (revert if not executed within time)
- Implement commit-reveal schemes for sensitive operations

**Timing Strategies:**
- Submit transactions during low MEV activity periods
- Use random delays to avoid predictable patterns
- Bundle transactions with MEV searchers cooperatively

## 6. Drawdown Management

**Purpose:** Monitor and limit portfolio drawdown to preserve capital during adverse market conditions.

### Drawdown Calculation

```python
from datetime import datetime, timedelta
from typing import List, Tuple

@dataclass
class PortfolioSnapshot:
    timestamp: datetime
    total_value: float

class DrawdownMonitor:
    """Monitor portfolio drawdown and enforce limits"""

    def __init__(self, max_drawdown_pct: float = 20.0):
        self.max_drawdown_pct = max_drawdown_pct
        self.snapshots: List[PortfolioSnapshot] = []
        self.peak_value = 0.0

    def add_snapshot(self, snapshot: PortfolioSnapshot):
        """Add new portfolio value snapshot"""
        self.snapshots.append(snapshot)
        self.peak_value = max(self.peak_value, snapshot.total_value)

    def calculate_current_drawdown(self) -> dict:
        """Calculate current drawdown from peak"""
        if not self.snapshots:
            return {"current_drawdown_pct": 0.0, "status": "no_data"}

        current_value = self.snapshots[-1].total_value
        drawdown_pct = ((self.peak_value - current_value) / self.peak_value) * 100

        return {
            "peak_value": self.peak_value,
            "current_value": current_value,
            "current_drawdown_pct": drawdown_pct,
            "max_allowed_pct": self.max_drawdown_pct,
            "remaining_buffer_pct": self.max_drawdown_pct - drawdown_pct,
            "status": self._get_drawdown_status(drawdown_pct)
        }

    def _get_drawdown_status(self, drawdown_pct: float) -> str:
        """Get current drawdown risk status"""
        if drawdown_pct < self.max_drawdown_pct * 0.5:
            return "healthy"
        elif drawdown_pct < self.max_drawdown_pct * 0.75:
            return "warning"
        elif drawdown_pct < self.max_drawdown_pct:
            return "danger"
        else:
            return "limit_exceeded"

    def should_halt_trading(self) -> bool:
        """Check if trading should be halted due to drawdown"""
        status = self.calculate_current_drawdown()
        return status["status"] == "limit_exceeded"

    def calculate_max_drawdown_period(
        self,
        lookback_days: int = 90
    ) -> dict:
        """Calculate maximum drawdown over period"""
        if len(self.snapshots) < 2:
            return {"max_drawdown_pct": 0.0, "period": "insufficient_data"}

        cutoff = datetime.now() - timedelta(days=lookback_days)
        period_snapshots = [
            s for s in self.snapshots if s.timestamp >= cutoff
        ]

        if not period_snapshots:
            return {"max_drawdown_pct": 0.0, "period": "no_data"}

        max_dd = 0.0
        peak = period_snapshots[0].total_value
        peak_date = period_snapshots[0].timestamp
        trough_date = peak_date

        for snapshot in period_snapshots:
            if snapshot.total_value > peak:
                peak = snapshot.total_value
                peak_date = snapshot.timestamp
            else:
                dd = ((peak - snapshot.total_value) / peak) * 100
                if dd > max_dd:
                    max_dd = dd
                    trough_date = snapshot.timestamp

        return {
            "max_drawdown_pct": max_dd,
            "peak_value": peak,
            "peak_date": peak_date.isoformat(),
            "trough_date": trough_date.isoformat(),
            "lookback_days": lookback_days
        }

# Usage Example
monitor = DrawdownMonitor(max_drawdown_pct=20.0)

# Add snapshots
monitor.add_snapshot(PortfolioSnapshot(datetime.now(), 100000.0))
monitor.add_snapshot(PortfolioSnapshot(datetime.now(), 85000.0))

status = monitor.calculate_current_drawdown()
# Result: 15% drawdown, WARNING status, 5% buffer remaining

if monitor.should_halt_trading():
    print("Trading halted: Maximum drawdown exceeded")
```

### Drawdown Protection Rules

**Risk Reduction Triggers:**
- **10% Drawdown:** Reduce position sizes by 25%
- **15% Drawdown:** Reduce position sizes by 50%
- **20% Drawdown:** Halt all new positions, close riskiest trades
- **25% Drawdown:** Emergency liquidation, preserve remaining capital

**Recovery Strategy:**
- Resume normal trading after 5% recovery from trough
- Start with reduced position sizes (50% of normal)
- Gradually increase exposure over 30 days
- Re-evaluate risk parameters after drawdown events

## Integration with Crypto Agent Architect

### Risk Manager Integration

**Location in Architecture:** Layer 3 (Trading Strategy)

**Integration Points:**

```python
from crypto_risk_management import (
    KellyPositionSizer,
    LiquidationMonitor,
    GasOptimizer,
    SlippageController,
    DrawdownMonitor
)

class CryptoAgentRiskManager:
    """Unified risk management for crypto trading agent"""

    def __init__(self, config: dict):
        # Initialize all risk components
        self.position_sizer = KellyPositionSizer(
            metrics=config["trading_metrics"],
            fractional_kelly=config.get("fractional_kelly", 0.25)
        )

        self.liquidation_monitor = LiquidationMonitor(
            position=config["leveraged_position"]
        )

        self.gas_optimizer = GasOptimizer(
            w3=config["web3_instance"],
            network=config.get("network", "mainnet")
        )

        self.slippage_controller = SlippageController(
            max_slippage_pct=config.get("max_slippage", 0.5)
        )

        self.drawdown_monitor = DrawdownMonitor(
            max_drawdown_pct=config.get("max_drawdown", 20.0)
        )

    def validate_trade(self, trade_params: dict) -> dict:
        """Validate trade against all risk checks"""

        # Check drawdown limit
        if self.drawdown_monitor.should_halt_trading():
            return {
                "approved": False,
                "reason": "Maximum drawdown exceeded",
                "risk_type": "drawdown"
            }

        # Check position size
        position = self.position_sizer.get_position_size(
            signal_confidence=trade_params.get("confidence", 1.0)
        )

        if position["position_usd"] < trade_params["min_position_size"]:
            return {
                "approved": False,
                "reason": "Position size too small (Kelly Criterion)",
                "risk_type": "position_sizing"
            }

        # Check liquidation risk (for leveraged trades)
        if trade_params.get("leverage", 1) > 1:
            risk = self.liquidation_monitor.assess_risk(
                current_price=trade_params["current_price"]
            )
            if risk["risk_level"] in ["danger", "critical"]:
                return {
                    "approved": False,
                    "reason": "Liquidation risk too high",
                    "risk_type": "liquidation"
                }

        # Check gas costs (for on-chain trades)
        if trade_params.get("on_chain", False):
            gas_check = self.gas_optimizer.should_execute_transaction(
                tx_type=trade_params["tx_type"],
                expected_profit_usd=trade_params["expected_profit"],
                eth_price_usd=trade_params["eth_price"]
            )
            if not gas_check["should_execute"]:
                return {
                    "approved": False,
                    "reason": "Gas costs exceed profitability threshold",
                    "risk_type": "gas_costs"
                }

        # All checks passed
        return {
            "approved": True,
            "position_size_usd": position["position_usd"],
            "max_loss_usd": position["max_loss_usd"],
            "risk_checks_passed": [
                "drawdown", "position_sizing", "liquidation", "gas_costs"
            ]
        }
```

### Real-Time Risk Monitoring

**Monitoring Loop:**

```python
import asyncio

async def risk_monitoring_loop(risk_manager: CryptoAgentRiskManager):
    """Continuous risk monitoring"""
    while True:
        # Check drawdown every 5 minutes
        drawdown = risk_manager.drawdown_monitor.calculate_current_drawdown()
        if drawdown["status"] in ["danger", "limit_exceeded"]:
            await alert_risk_team(drawdown)

        # Check liquidation risk every 30 seconds
        if hasattr(risk_manager, 'liquidation_monitor'):
            liq_risk = risk_manager.liquidation_monitor.assess_risk(
                current_price=await get_current_price()
            )
            if liq_risk["risk_level"] == "critical":
                await emergency_position_close()

        await asyncio.sleep(30)
```

## Resources

### Scripts

**C:\Users\x8333\Desktop\AI_PJT\my-skills\crypto-risk-management\scripts\**

- `risk_calculator.py` - All-in-one risk calculation utilities (Kelly, liquidation, slippage, drawdown)
- `liquidation_monitor.py` - Real-time liquidation monitoring daemon
- `gas_optimizer.py` - Gas price fetching and optimization decisions

### References

**C:\Users\x8333\Desktop\AI_PJT\my-skills\crypto-risk-management\references\**

- `risk_metrics.md` - Detailed risk metric definitions and formulas
- `position_sizing_guide.md` - Comprehensive Kelly Criterion guide with examples

## Best Practices

### Risk Management Hierarchy

1. **Capital Preservation:** Never risk total portfolio loss
2. **Position Sizing:** Use Kelly Criterion with fractional multiplier
3. **Stop Losses:** Always set stop-loss orders (max 2% per trade)
4. **Diversification:** Max 10% in any single position
5. **Drawdown Limits:** Halt trading at 20% portfolio drawdown

### Monitoring Frequency

- **Liquidation Risk:** Every 30 seconds for leveraged positions
- **Drawdown:** Every 5 minutes during trading hours
- **Gas Prices:** Every 1 minute for on-chain strategies
- **Slippage:** Per-trade validation before execution
- **Position Sizing:** Recalculate every 50-100 trades

### Emergency Protocols

**Circuit Breakers:**
- Halt all trading if drawdown exceeds 20%
- Close all leveraged positions if any reach critical liquidation risk
- Pause on-chain trading if gas prices exceed 200 gwei (unless critical)
- Reject trades with slippage >5% regardless of tolerance settings

**Recovery Procedures:**
- Document all emergency events with full context
- Conduct post-mortem analysis within 24 hours
- Adjust risk parameters based on lessons learned
- Resume trading gradually with reduced position sizes
