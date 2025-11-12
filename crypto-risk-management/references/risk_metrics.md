# Crypto Risk Management Metrics

Comprehensive reference for risk metric definitions, formulas, and interpretation.

## Position Sizing Metrics

### Kelly Criterion

**Purpose:** Calculate optimal position size to maximize long-term capital growth.

**Formula:**
```
Kelly % = (Win Rate × Avg Win - Loss Rate × Avg Loss) / Avg Win

Where:
- Win Rate = Wins / Total Trades
- Loss Rate = Losses / Total Trades
- Avg Win = Average winning trade return (as decimal, e.g., 0.05 = 5%)
- Avg Loss = Average losing trade return (as decimal, e.g., -0.03 = -3%)
```

**Fractional Kelly:**
```
Fractional Kelly = Kelly % × Fraction (typically 0.25 to 0.5)
```

**Example:**
```
Total Trades: 100
Wins: 60
Losses: 40
Avg Win: 8% (0.08)
Avg Loss: -5% (-0.05)

Win Rate = 60/100 = 0.6
Loss Rate = 40/100 = 0.4

Kelly % = (0.6 × 0.08 - 0.4 × 0.05) / 0.08
        = (0.048 - 0.02) / 0.08
        = 0.028 / 0.08
        = 0.35 (35%)

Fractional Kelly (25%) = 0.35 × 0.25 = 0.0875 (8.75%)

For $100,000 portfolio: $8,750 per position
```

**Interpretation:**
- **Kelly > 20%:** Excellent trading system, but use fractional Kelly
- **Kelly 10-20%:** Good system, use 25-50% fractional Kelly
- **Kelly 5-10%:** Decent system, use 25% fractional Kelly
- **Kelly < 5%:** Weak edge, consider improving strategy
- **Kelly < 0%:** Losing strategy, do not trade

**Risk Controls:**
- Never use full Kelly (too aggressive, high volatility)
- Cap maximum position at 10% of portfolio
- Adjust for signal confidence (multiply by confidence score)
- Recalculate every 50-100 trades

---

## Liquidation Risk Metrics

### Liquidation Price

**Purpose:** Calculate price level at which leveraged position will be forcibly closed.

**For Long Positions:**
```
Liquidation Price = Entry Price × (1 - Initial Margin / Leverage)
```

**For Short Positions:**
```
Liquidation Price = Entry Price × (1 + Initial Margin / Leverage)
```

**Example (Long Position):**
```
Entry Price: $50,000
Leverage: 10x
Initial Margin: $5,000

Liquidation Price = $50,000 × (1 - $5,000 / 10)
                  = $50,000 × (1 - 0.1)
                  = $50,000 × 0.9
                  = $45,000
```

**Example (Short Position):**
```
Entry Price: $50,000
Leverage: 10x
Initial Margin: $5,000

Liquidation Price = $50,000 × (1 + 0.1)
                  = $50,000 × 1.1
                  = $55,000
```

### Distance to Liquidation

**Purpose:** Measure how close current price is to liquidation.

**For Long Positions:**
```
Distance % = ((Current Price - Liquidation Price) / Current Price) × 100
```

**For Short Positions:**
```
Distance % = ((Liquidation Price - Current Price) / Current Price) × 100
```

**Risk Levels:**
- **>20%:** Safe - normal monitoring
- **10-20%:** Warning - add margin or reduce position 25%
- **5-10%:** Danger - reduce position 50% immediately
- **<5%:** Critical - close entire position at market

---

## Gas Cost Metrics

### Gas Cost Calculation (EIP-1559)

**Purpose:** Calculate transaction cost on Ethereum post-EIP-1559.

**Formula:**
```
Total Gas Cost (Wei) = Gas Limit × (Base Fee + Priority Fee)
Total Gas Cost (ETH) = Total Gas Cost (Wei) / 10^18
Total Gas Cost (USD) = Total Gas Cost (ETH) × ETH Price
```

**Gas Limits by Transaction Type:**
- Simple Transfer: 21,000 gas
- ERC-20 Transfer: 65,000 gas
- ERC-20 Approve: 45,000 gas
- Uniswap V2 Swap: 150,000 gas
- Uniswap V3 Swap: 180,000 gas
- Complex DeFi: 300,000+ gas

**Example:**
```
Transaction: Uniswap V2 Swap
Gas Limit: 150,000
Base Fee: 30 Gwei
Priority Fee: 1.5 Gwei
ETH Price: $3,000

Max Fee = 30 + 1.5 = 31.5 Gwei
Total Cost = 150,000 × 31.5 Gwei
          = 4,725,000 Gwei
          = 0.004725 ETH
          = $14.18 USD
```

### Gas Optimization Score

**Purpose:** Determine if transaction is economically viable.

**Formula:**
```
Profit Ratio = Expected Profit / Gas Cost

Should Execute = Profit Ratio ≥ Minimum Threshold (typically 2.0)
```

**Example:**
```
Expected Profit: $50
Gas Cost: $15
Profit Ratio = $50 / $15 = 3.33

Decision: Execute (ratio > 2.0)
```

**Thresholds:**
- **Ratio > 3.0:** Excellent opportunity
- **Ratio 2.0-3.0:** Good opportunity
- **Ratio 1.5-2.0:** Marginal, consider waiting
- **Ratio < 1.5:** Not worth executing

---

## Slippage Metrics

### Slippage Percentage

**Purpose:** Measure price difference between expected and executed price.

**Formula:**
```
Slippage % = |Executed Price - Expected Price| / Expected Price × 100
```

**Example (Buy Order):**
```
Expected Price: $50,000
Executed Price: $50,150
Slippage = |$50,150 - $50,000| / $50,000 × 100
         = $150 / $50,000 × 100
         = 0.3%
```

### DEX Price Impact

**Purpose:** Estimate slippage for DEX trades using constant product formula.

**Simplified Formula:**
```
Size Ratio = Trade Size / Pool Liquidity
Price Impact % = (Size Ratio / (1 - Size Ratio)) × 100
Total Slippage % = Price Impact % + Pool Fee %
```

**Example:**
```
Trade Size: $10,000
Pool Liquidity: $1,000,000
Pool Fee: 0.3%

Size Ratio = $10,000 / $1,000,000 = 0.01
Price Impact = (0.01 / (1 - 0.01)) × 100
             = (0.01 / 0.99) × 100
             = 1.01%

Total Slippage = 1.01% + 0.3% = 1.31%
```

**Acceptable Slippage:**
- **<0.5%:** Excellent execution
- **0.5-1.0%:** Good execution
- **1.0-2.0%:** Acceptable for medium trades
- **2.0-5.0%:** High slippage, consider splitting order
- **>5.0%:** Excessive, do not execute

---

## Drawdown Metrics

### Drawdown Percentage

**Purpose:** Measure decline from peak portfolio value.

**Formula:**
```
Drawdown % = ((Peak Value - Current Value) / Peak Value) × 100
```

**Example:**
```
Peak Value: $100,000
Current Value: $85,000

Drawdown = (($100,000 - $85,000) / $100,000) × 100
         = $15,000 / $100,000 × 100
         = 15%
```

### Maximum Drawdown (MDD)

**Purpose:** Calculate worst peak-to-trough decline over a period.

**Formula:**
```
MDD = Max(Peak_i - Trough_j) / Peak_i × 100
where j > i (trough occurs after peak)
```

**Interpretation:**
- **<10%:** Excellent risk management
- **10-20%:** Good risk management
- **20-30%:** Moderate risk, review strategy
- **30-50%:** High risk, significant review needed
- **>50%:** Severe, emergency measures required

### Recovery Time

**Purpose:** Measure time to recover from drawdown.

**Formula:**
```
Recovery Time = Days from Trough to New Peak
```

**Typical Recovery Times:**
- **5-10% Drawdown:** 7-30 days
- **10-20% Drawdown:** 30-90 days
- **20-30% Drawdown:** 90-180 days
- **>30% Drawdown:** 180+ days

---

## Risk-Adjusted Performance Metrics

### Sharpe Ratio

**Purpose:** Measure risk-adjusted return.

**Formula:**
```
Sharpe Ratio = (Portfolio Return - Risk-Free Rate) / Portfolio Volatility
```

**Interpretation:**
- **>3.0:** Exceptional
- **2.0-3.0:** Very good
- **1.0-2.0:** Good
- **0.5-1.0:** Acceptable
- **<0.5:** Poor

### Sortino Ratio

**Purpose:** Measure risk-adjusted return using downside deviation.

**Formula:**
```
Sortino Ratio = (Portfolio Return - Risk-Free Rate) / Downside Deviation
```

**Better than Sharpe because it only penalizes downside volatility.**

**Interpretation:**
- **>2.0:** Excellent
- **1.0-2.0:** Good
- **0.5-1.0:** Acceptable
- **<0.5:** Poor

### Maximum Adverse Excursion (MAE)

**Purpose:** Measure worst unrealized loss during a trade.

**Formula:**
```
MAE % = (Entry Price - Worst Price) / Entry Price × 100
```

**Use Case:** Set stop-loss levels based on historical MAE.

---

## Risk Limits and Thresholds

### Position Size Limits

| Limit Type | Threshold | Rationale |
|------------|-----------|-----------|
| Max Single Position | 10% | Diversification |
| Max Total Exposure | 50% | Capital preservation |
| Min Position Size | 0.1% or $100 | Avoid dust trades |
| Max Correlated Positions | 20% | Correlation risk |

### Leverage Limits

| Account Size | Max Leverage | Rationale |
|--------------|--------------|-----------|
| < $10,000 | 2x | Capital preservation |
| $10,000 - $50,000 | 3x | Moderate risk |
| $50,000 - $100,000 | 5x | Experienced traders |
| > $100,000 | 10x | Professional only |

### Drawdown Action Triggers

| Drawdown Level | Action |
|----------------|--------|
| 10% | Reduce position sizes by 25% |
| 15% | Reduce position sizes by 50% |
| 20% | Halt new positions, close riskiest trades |
| 25% | Emergency liquidation |

---

## Monitoring Frequencies

| Risk Type | Monitoring Frequency | Alert Threshold |
|-----------|---------------------|-----------------|
| Liquidation Risk | Every 30 seconds | Distance < 10% |
| Drawdown | Every 5 minutes | Drawdown > 15% |
| Gas Prices | Every 1 minute | Gas > 100 Gwei |
| Slippage | Per-trade validation | Slippage > 1% |
| Position Sizing | Every 50 trades | Win rate < 50% |
| Portfolio Correlation | Daily | Correlation > 0.7 |

---

## Emergency Protocols

### Circuit Breakers

1. **Drawdown Limit:** Halt all trading if drawdown exceeds 20%
2. **Liquidation Risk:** Close all positions with distance < 5%
3. **Gas Cost Spike:** Pause on-chain trading if gas > 200 Gwei (unless critical)
4. **Slippage Spike:** Reject trades with slippage > 5% regardless of tolerance

### Recovery Procedures

1. Document emergency event with full context
2. Conduct post-mortem analysis within 24 hours
3. Adjust risk parameters based on lessons learned
4. Resume trading gradually with 50% normal position sizes
5. Increase exposure over 30 days if performance stabilizes
