# Position Sizing Guide: Kelly Criterion for Crypto Trading

Comprehensive guide to optimal position sizing using Kelly Criterion with practical examples and risk controls.

## Overview

Kelly Criterion is a mathematical formula for determining optimal position size to maximize long-term capital growth. Originally developed for gambling and investment portfolios, it's particularly useful for crypto trading where volatility and uncertainty are high.

**Key Principle:** Size positions to maximize geometric growth of capital over time, not arithmetic returns.

---

## The Kelly Formula

### Basic Formula

```
Kelly % = (Win Rate × Avg Win - Loss Rate × Avg Loss) / Avg Win
```

**Variables:**
- **Win Rate:** Percentage of winning trades (e.g., 0.60 = 60%)
- **Loss Rate:** Percentage of losing trades (e.g., 0.40 = 40%)
- **Avg Win:** Average winning trade return as decimal (e.g., 0.08 = 8%)
- **Avg Loss:** Average losing trade return as decimal (e.g., -0.05 = -5%)

### Fractional Kelly

**Problem:** Full Kelly is too aggressive and leads to high volatility.

**Solution:** Use a fraction of Kelly, typically 25% to 50%.

```
Position Size = Kelly % × Fractional Multiplier × Portfolio Value
```

**Recommended Multipliers:**
- **Conservative (0.25):** Reduces volatility by 75%, suitable for most traders
- **Moderate (0.50):** Reduces volatility by 50%, for experienced traders
- **Aggressive (0.75):** Only for professional traders with proven edge

---

## Step-by-Step Calculation

### Step 1: Collect Historical Data

Analyze last 50-100 trades to calculate:

**Example Data:**
```
Total Trades: 100
Winning Trades: 60
Losing Trades: 40
Sum of Winning Returns: 4.8 (60 trades × 8% average)
Sum of Losing Returns: -2.0 (40 trades × 5% average loss)
```

### Step 2: Calculate Metrics

**Win Rate:**
```
Win Rate = 60 / 100 = 0.60 (60%)
```

**Loss Rate:**
```
Loss Rate = 40 / 100 = 0.40 (40%)
```

**Average Win:**
```
Avg Win = 4.8 / 60 = 0.08 (8%)
```

**Average Loss:**
```
Avg Loss = -2.0 / 40 = -0.05 (-5%)
```

### Step 3: Apply Kelly Formula

```
Kelly % = (0.60 × 0.08 - 0.40 × 0.05) / 0.08
        = (0.048 - 0.020) / 0.08
        = 0.028 / 0.08
        = 0.35 (35%)
```

**Interpretation:** Optimal position size is 35% of portfolio per trade.

### Step 4: Apply Fractional Kelly

**Using 0.25 fractional multiplier:**
```
Fractional Kelly = 0.35 × 0.25 = 0.0875 (8.75%)
```

### Step 5: Calculate Position Size

**For $100,000 portfolio:**
```
Position Size = $100,000 × 0.0875 = $8,750
```

---

## Practical Examples

### Example 1: Conservative Trader

**Profile:**
- Portfolio: $50,000
- Win Rate: 55%
- Avg Win: 6%
- Avg Loss: -4%
- Fractional Kelly: 0.25

**Calculation:**
```
Kelly % = (0.55 × 0.06 - 0.45 × 0.04) / 0.06
        = (0.033 - 0.018) / 0.06
        = 0.015 / 0.06
        = 0.25 (25%)

Fractional Kelly = 0.25 × 0.25 = 0.0625 (6.25%)
Position Size = $50,000 × 0.0625 = $3,125
```

**Result:** Risk $3,125 per trade with max loss of $125 (-4%).

### Example 2: Aggressive Trader

**Profile:**
- Portfolio: $200,000
- Win Rate: 65%
- Avg Win: 10%
- Avg Loss: -6%
- Fractional Kelly: 0.50

**Calculation:**
```
Kelly % = (0.65 × 0.10 - 0.35 × 0.06) / 0.10
        = (0.065 - 0.021) / 0.10
        = 0.044 / 0.10
        = 0.44 (44%)

Fractional Kelly = 0.44 × 0.50 = 0.22 (22%)
Position Size = $200,000 × 0.22 = $44,000
```

**But apply max position limit of 10%:**
```
Final Position Size = $200,000 × 0.10 = $20,000
```

**Result:** Risk $20,000 per trade (capped at 10% limit).

### Example 3: Confidence-Adjusted Position

**Profile:**
- Base Position Size: $10,000 (from Kelly calculation)
- Signal Confidence Levels:
  - High Confidence (90%): Multiply by 1.0
  - Medium Confidence (70%): Multiply by 0.7
  - Low Confidence (50%): Multiply by 0.5

**Calculations:**
```
High Confidence Trade:
Position = $10,000 × 1.0 = $10,000

Medium Confidence Trade:
Position = $10,000 × 0.7 = $7,000

Low Confidence Trade:
Position = $10,000 × 0.5 = $5,000
```

---

## Risk Controls and Limits

### Hard Limits

**1. Maximum Single Position: 10% of Portfolio**

Even if Kelly suggests 20%, cap at 10% to maintain diversification.

```python
final_position_pct = min(kelly_pct, 0.10)
```

**2. Maximum Total Exposure: 50% of Portfolio**

Never have more than 50% deployed across all positions.

**3. Minimum Position Size: 0.1% or $100**

Avoid dust trades that incur excessive fees relative to potential profit.

**4. Maximum Correlated Positions: 20% Combined**

If positions are correlated (e.g., BTC and ETH), limit combined exposure.

### Dynamic Adjustments

**1. Drawdown-Based Reduction**

Scale down position sizes during drawdown periods:

```
Adjustment Factor = 1 - (Current Drawdown / Max Drawdown)

If portfolio is down 15% from peak with max allowed of 20%:
Adjustment = 1 - (15 / 20) = 0.25

Reduce all positions by 75% (multiply by 0.25)
```

**2. Volatility-Based Adjustment**

Increase position size during low volatility, decrease during high volatility:

```
Volatility Ratio = Current Volatility / Average Volatility

If current vol is 2x average:
Position Multiplier = 1 / 2 = 0.5 (reduce size by 50%)
```

**3. Win Streak / Loss Streak Adjustment**

After consecutive losses, temporarily reduce position sizes:

```
After 3 consecutive losses: Reduce by 25%
After 5 consecutive losses: Reduce by 50%
After 7 consecutive losses: Stop trading, review strategy
```

---

## Common Mistakes and How to Avoid Them

### Mistake 1: Using Full Kelly

**Problem:** Full Kelly leads to extreme volatility (up to 50% drawdowns).

**Solution:** Always use fractional Kelly (0.25-0.50).

**Example:**
```
Full Kelly Position: $35,000 (35% of $100k)
25% Fractional Kelly: $8,750 (8.75% of $100k)

After 10% loss on full Kelly position: -$3,500 (3.5% portfolio loss)
After 10% loss on fractional Kelly: -$875 (0.875% portfolio loss)
```

### Mistake 2: Using Outdated Metrics

**Problem:** Win rate and average win/loss change over time.

**Solution:** Recalculate Kelly every 50-100 trades.

**Monitoring:**
```
Track rolling 50-trade window:
- If win rate drops 10%+ → Recalculate
- If avg win/loss changes 20%+ → Recalculate
- Every month → Review and recalculate
```

### Mistake 3: Ignoring Correlation

**Problem:** Multiple correlated positions increase concentration risk.

**Solution:** Adjust position sizes for correlation.

**Example:**
```
BTC Position: $10,000
ETH Position: $10,000
Correlation: 0.8

Effective Exposure = $10,000 + ($10,000 × 0.8) = $18,000
Combined risk is higher than $20,000 independent positions
```

### Mistake 4: No Maximum Position Limit

**Problem:** Kelly can suggest very large positions with strong edge.

**Solution:** Always cap at 10% per position.

**Example:**
```
Kelly suggests 30% position
Without cap: $30,000 position on $100k portfolio (too risky)
With 10% cap: $10,000 position (properly diversified)
```

### Mistake 5: Ignoring Transaction Costs

**Problem:** High fees reduce actual returns.

**Solution:** Adjust average win/loss for costs.

**Example:**
```
Avg Win Before Fees: 8%
Trading Fees: 0.2%
Effective Avg Win: 7.8%

Avg Loss Before Fees: -5%
Trading Fees: 0.2%
Effective Avg Loss: -5.2%

Recalculate Kelly with adjusted figures
```

---

## Implementation Checklist

### Initial Setup

- [ ] Collect last 100 trades data
- [ ] Calculate win rate and loss rate
- [ ] Calculate average win and average loss
- [ ] Determine fractional Kelly multiplier (start with 0.25)
- [ ] Set maximum position limit (10%)
- [ ] Set maximum total exposure (50%)
- [ ] Set minimum position size ($100 or 0.1%)

### Per-Trade Execution

- [ ] Calculate base Kelly position size
- [ ] Apply fractional multiplier
- [ ] Adjust for signal confidence
- [ ] Check against maximum position limit
- [ ] Verify total portfolio exposure < 50%
- [ ] Ensure position size > minimum
- [ ] Calculate expected maximum loss
- [ ] Document position size rationale

### Periodic Review (Monthly)

- [ ] Recalculate Kelly metrics from last 50-100 trades
- [ ] Review win rate trend
- [ ] Review average win/loss trend
- [ ] Adjust fractional multiplier if needed
- [ ] Review maximum drawdown
- [ ] Evaluate if limits need adjustment
- [ ] Document changes and reasoning

---

## Kelly Criterion vs. Fixed Percentage

### Fixed Percentage (e.g., always 5%)

**Pros:**
- Simple to implement
- Consistent across all trades
- Easy to understand

**Cons:**
- Doesn't account for edge strength
- Suboptimal capital growth
- Same size for strong and weak signals

### Kelly Criterion

**Pros:**
- Optimizes long-term capital growth
- Scales with edge strength
- Adjusts for confidence levels

**Cons:**
- Requires accurate metrics
- More complex to calculate
- Can suggest aggressive sizes

**Best Practice:** Use Kelly Criterion with 25% fractional multiplier for optimal risk-adjusted growth.

---

## Advanced Topics

### Multi-Asset Portfolio Kelly

When trading multiple uncorrelated assets, allocate Kelly percentage to each:

```
Total Kelly Allocation = Sum of individual Kelly %

If Kelly suggests 40% total across 4 assets:
Asset 1: 12% (Kelly = 12%)
Asset 2: 10% (Kelly = 10%)
Asset 3: 10% (Kelly = 10%)
Asset 4: 8% (Kelly = 8%)

Apply fractional Kelly to each:
Asset 1: 12% × 0.25 = 3%
Asset 2: 10% × 0.25 = 2.5%
Asset 3: 10% × 0.25 = 2.5%
Asset 4: 8% × 0.25 = 2%

Total Exposure: 10% (conservative)
```

### Kelly with Stop-Loss Orders

Adjust average loss for stop-loss placement:

```
Average Loss = Max Loss from Stop-Loss

If stop-loss is set at 2%:
Avg Loss = -0.02 (even if historical is -5%)

Recalculate Kelly with adjusted loss figure
```

### Bayesian Kelly

Update Kelly as you gather more data:

```
Initial Kelly (50 trades): 25%
Updated Kelly (100 trades): 30%
Updated Kelly (200 trades): 28%

Use confidence intervals:
95% Confidence: Kelly is between 24% and 32%
Use lower bound (24%) for conservative sizing
```

---

## Summary

**Key Takeaways:**

1. **Always use Fractional Kelly** (0.25-0.50, never full Kelly)
2. **Set hard limits** (max 10% per position, 50% total exposure)
3. **Recalculate regularly** (every 50-100 trades or monthly)
4. **Adjust for confidence** (scale down low-confidence trades)
5. **Account for correlation** (reduce size for correlated positions)
6. **Monitor drawdown** (reduce sizes during losing streaks)
7. **Include transaction costs** (adjust avg win/loss for fees)
8. **Use stop-losses** (Kelly assumes unlimited loss without stops)

**Recommended Starting Configuration:**
- Fractional Kelly: 0.25
- Max Single Position: 10%
- Max Total Exposure: 50%
- Min Position Size: $100 or 0.1%
- Recalculation Frequency: Every 50 trades

**Remember:** Kelly Criterion optimizes long-term growth but can be volatile. Use fractional Kelly and hard limits to balance growth with acceptable risk levels.
