# Backtesting Guide for Crypto Trading Strategies

Best practices, common pitfalls, and methodologies for accurate backtesting of cryptocurrency trading strategies.

## Table of Contents

1. [Core Principles](#core-principles)
2. [Data Requirements](#data-requirements)
3. [Execution Modeling](#execution-modeling)
4. [Common Pitfalls](#common-pitfalls)
5. [Performance Metrics](#performance-metrics)
6. [Validation Techniques](#validation-techniques)

## Core Principles

### 1. Realistic Assumptions

**Rule:** Assume worse execution than theoretical optimum

```python
# BAD: Perfect execution at close price
entry_price = candle.close

# GOOD: Realistic execution with slippage and fees
entry_price = candle.close * (1 + slippage_pct)
execution_fee = entry_price * quantity * fee_rate
total_cost = entry_price * quantity + execution_fee
```

### 2. Look-Ahead Bias Prevention

**Rule:** Only use data available at decision time

```python
# BAD: Using future data
signal = calculate_indicator(data)  # Uses entire dataset including future

# GOOD: Point-in-time calculation
signal = calculate_indicator(data.loc[:current_timestamp])
```

### 3. Survivorship Bias Avoidance

**Rule:** Include delisted/failed assets in universe

```python
# BAD: Only current top 100 coins
universe = get_current_top_100()

# GOOD: Historical top 100 at each timestamp
universe = get_historical_top_100(timestamp)
```

## Data Requirements

### Minimum Data Requirements

**Time Period:**
- Minimum: 1 year
- Recommended: 2-3 years
- Ideal: Full market cycle (bull + bear)

**Frequency:**
- Arbitrage: 1-second or tick data
- Market Making: 1-second with order book snapshots
- Momentum/Mean Reversion: 1-hour candles minimum
- Grid Trading: 5-minute candles

**Data Quality Checks:**

```python
def validate_data_quality(df: pd.DataFrame) -> bool:
    """Validate historical data quality"""

    checks = []

    # Check for missing timestamps
    expected_timestamps = pd.date_range(
        start=df.index.min(),
        end=df.index.max(),
        freq='1min'
    )
    missing_pct = 1 - len(df) / len(expected_timestamps)
    checks.append(missing_pct < 0.01)  # <1% missing

    # Check for price anomalies
    returns = df['close'].pct_change()
    outliers = returns[abs(returns) > 0.50].count()  # >50% moves
    checks.append(outliers < len(df) * 0.001)  # <0.1% outliers

    # Check for zero volume
    zero_volume = (df['volume'] == 0).sum()
    checks.append(zero_volume < len(df) * 0.05)  # <5% zero volume

    # Check for duplicate timestamps
    duplicates = df.index.duplicated().sum()
    checks.append(duplicates == 0)

    return all(checks)
```

## Execution Modeling

### 1. Fee Structure

**Maker/Taker Fees:**

```python
class FeeCalculator:
    """Calculate realistic trading fees"""

    def __init__(self, maker_fee: float = 0.001, taker_fee: float = 0.001):
        self.maker_fee = maker_fee
        self.taker_fee = taker_fee

    def calculate_fee(
        self,
        quantity: float,
        price: float,
        is_maker: bool
    ) -> float:
        """Calculate fee for trade"""

        notional = quantity * price
        fee_rate = self.maker_fee if is_maker else self.taker_fee

        return notional * fee_rate
```

**VIP Tier Discounts:**

```python
def get_fee_rate(thirty_day_volume: float) -> tuple[float, float]:
    """Get fee rate based on trading volume (Binance-like tiers)"""

    if thirty_day_volume >= 150_000_000:  # VIP 9: $150M+
        return 0.00012, 0.00030  # 0.012% maker, 0.03% taker
    elif thirty_day_volume >= 50_000_000:  # VIP 8: $50M+
        return 0.00016, 0.00035
    elif thirty_day_volume >= 15_000_000:  # VIP 7: $15M+
        return 0.00020, 0.00040
    # ... more tiers
    else:  # Regular
        return 0.00100, 0.00100  # 0.1% maker/taker
```

### 2. Slippage Modeling

**Market Impact:**

```python
def calculate_slippage(
    order_size_usd: float,
    daily_volume_usd: float,
    volatility: float
) -> float:
    """Calculate expected slippage based on order size and liquidity"""

    # Kyle's lambda: price impact coefficient
    # Larger orders relative to volume → more slippage
    volume_pct = order_size_usd / daily_volume_usd

    # Base slippage
    base_slippage = 0.0005  # 0.05%

    # Volume impact (square root model)
    volume_impact = 0.01 * np.sqrt(volume_pct)

    # Volatility impact
    volatility_impact = volatility * 0.1

    total_slippage = base_slippage + volume_impact + volatility_impact

    # Cap at 2% (extreme cases)
    return min(total_slippage, 0.02)
```

**Order Book Modeling:**

```python
def simulate_market_order_execution(
    order_book: dict,
    side: str,
    quantity: float
) -> tuple[float, float]:
    """Simulate market order walking through order book"""

    levels = order_book['asks'] if side == 'BUY' else order_book['bids']

    remaining = quantity
    total_cost = 0

    for price, size in levels:
        filled = min(remaining, size)
        total_cost += filled * price
        remaining -= filled

        if remaining == 0:
            break

    if remaining > 0:
        # Insufficient liquidity, model 1% extra slippage per 10% unfilled
        slippage_penalty = (remaining / quantity) * 0.10
        avg_price = total_cost / (quantity - remaining)
        total_cost += remaining * avg_price * (1 + slippage_penalty)

    avg_execution_price = total_cost / quantity
    slippage_pct = (avg_execution_price / levels[0][0] - 1)

    return avg_execution_price, slippage_pct
```

### 3. Latency and Execution Delays

```python
class ExecutionSimulator:
    """Simulate realistic execution delays"""

    def __init__(
        self,
        signal_latency_ms: int = 100,  # Time to generate signal
        network_latency_ms: int = 50,  # API round-trip
        exchange_latency_ms: int = 20  # Exchange processing
    ):
        self.total_latency_ms = (
            signal_latency_ms +
            network_latency_ms +
            exchange_latency_ms
        )

    def get_execution_price(
        self,
        signal_timestamp: pd.Timestamp,
        signal_price: float,
        market_data: pd.DataFrame
    ) -> float:
        """Get actual execution price after latency"""

        # Find price after latency delay
        execution_timestamp = signal_timestamp + pd.Timedelta(
            milliseconds=self.total_latency_ms
        )

        # Get next available price after execution timestamp
        future_data = market_data[market_data.index > execution_timestamp]

        if len(future_data) == 0:
            return None  # No data available (end of dataset)

        # Use open of next candle (realistic execution price)
        execution_price = future_data.iloc[0]['open']

        return execution_price
```

## Common Pitfalls

### 1. Overfitting

**Problem:** Strategy optimized for specific historical period

**Detection:**

```python
def detect_overfitting(
    train_sharpe: float,
    test_sharpe: float,
    num_parameters: int,
    num_trades: int
) -> bool:
    """Detect if strategy is overfitted"""

    # Rule 1: Large performance degradation
    sharpe_drop = (train_sharpe - test_sharpe) / train_sharpe
    if sharpe_drop > 0.30:  # >30% degradation
        return True

    # Rule 2: Too many parameters relative to trades
    if num_parameters > num_trades / 20:  # <20 trades per parameter
        return True

    # Rule 3: Too-perfect training performance
    if train_sharpe > 5.0:  # Unrealistic Sharpe
        return True

    return False
```

**Prevention:**
- Use simple strategies with few parameters
- Require minimum 100 trades per parameter
- Walk-forward optimization
- Out-of-sample testing

### 2. Survivor Bias

**Problem:** Only backtesting on coins that survived to present

**Solution:**

```python
def get_universe_at_timestamp(
    timestamp: pd.Timestamp,
    criteria: dict
) -> List[str]:
    """Get trading universe at specific timestamp (no survivor bias)"""

    # Load historical market cap rankings
    historical_rankings = load_historical_cmc_rankings(timestamp)

    # Filter by criteria at that specific time
    universe = [
        coin['symbol']
        for coin in historical_rankings
        if coin['market_cap'] >= criteria['min_market_cap']
        and coin['volume_24h'] >= criteria['min_volume']
        and coin['age_days'] >= criteria['min_age']
    ]

    return universe
```

### 3. Look-Ahead Bias

**Problem:** Using future information in historical decisions

**Detection:**

```python
def check_for_lookahead_bias(strategy_code: str) -> List[str]:
    """Scan strategy code for common look-ahead patterns"""

    warnings = []

    # Check for using full dataset without time filtering
    if '.iloc[-1]' in strategy_code and '.loc[:current_time]' not in strategy_code:
        warnings.append("Potential look-ahead: using .iloc[-1] without time filtering")

    # Check for calculating indicators on full dataset
    if 'calculate_indicator(data)' in strategy_code:
        warnings.append("Potential look-ahead: indicators should use .loc[:current_time]")

    # Check for using close price before candle completes
    if 'entry_price = candle.close' in strategy_code:
        warnings.append("Look-ahead: can't know close price until candle completes")

    return warnings
```

**Prevention:**
- Only use data available at decision time
- Use point-in-time database snapshots
- Trade on candle open, not close

### 4. Data Quality Issues

**Problem:** Incorrect or missing data

**Detection:**

```python
def detect_data_issues(df: pd.DataFrame) -> Dict[str, List]:
    """Comprehensive data quality checks"""

    issues = {
        'missing_data': [],
        'price_anomalies': [],
        'volume_anomalies': [],
        'timestamp_issues': []
    }

    # Missing data
    for col in ['open', 'high', 'low', 'close', 'volume']:
        missing = df[col].isna().sum()
        if missing > 0:
            issues['missing_data'].append(f"{col}: {missing} missing values")

    # Price anomalies (gaps >50%)
    for col in ['open', 'high', 'low', 'close']:
        returns = df[col].pct_change()
        anomalies = returns[abs(returns) > 0.50]
        if len(anomalies) > 0:
            issues['price_anomalies'].append(
                f"{col}: {len(anomalies)} suspicious price moves"
            )

    # Volume anomalies (sudden 100x spikes)
    volume_ratio = df['volume'] / df['volume'].rolling(24).median()
    spikes = volume_ratio[volume_ratio > 100]
    if len(spikes) > 0:
        issues['volume_anomalies'].append(f"{len(spikes)} volume spikes")

    # Timestamp issues
    time_diffs = df.index.to_series().diff()
    expected_diff = pd.Timedelta(minutes=1)  # Assuming 1-min data
    irregular = time_diffs[time_diffs != expected_diff]
    if len(irregular) > len(df) * 0.05:  # >5% irregular
        issues['timestamp_issues'].append(f"{len(irregular)} irregular timestamps")

    return issues
```

## Performance Metrics

### Essential Metrics

```python
class PerformanceAnalyzer:
    """Calculate comprehensive performance metrics"""

    def __init__(self, trades: List[Trade], equity_curve: pd.Series):
        self.trades = trades
        self.equity_curve = equity_curve

    def calculate_all_metrics(self) -> Dict:
        """Calculate all performance metrics"""

        return {
            'returns': self.total_return(),
            'cagr': self.cagr(),
            'sharpe_ratio': self.sharpe_ratio(),
            'sortino_ratio': self.sortino_ratio(),
            'calmar_ratio': self.calmar_ratio(),
            'max_drawdown': self.max_drawdown(),
            'win_rate': self.win_rate(),
            'profit_factor': self.profit_factor(),
            'expectancy': self.expectancy(),
            'num_trades': len(self.trades),
            'avg_trade_duration': self.avg_trade_duration()
        }

    def sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:
        """Calculate Sharpe ratio"""
        returns = self.equity_curve.pct_change().dropna()
        excess_returns = returns - risk_free_rate / 252  # Daily risk-free

        if returns.std() == 0:
            return 0.0

        return np.sqrt(252) * excess_returns.mean() / returns.std()

    def sortino_ratio(self, target_return: float = 0.0) -> float:
        """Calculate Sortino ratio (downside deviation only)"""
        returns = self.equity_curve.pct_change().dropna()
        excess_returns = returns - target_return / 252

        downside_returns = returns[returns < target_return]
        downside_std = downside_returns.std()

        if downside_std == 0:
            return 0.0

        return np.sqrt(252) * excess_returns.mean() / downside_std

    def max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        cumulative = (1 + self.equity_curve.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max

        return drawdown.min()

    def win_rate(self) -> float:
        """Calculate percentage of winning trades"""
        if len(self.trades) == 0:
            return 0.0

        winning_trades = sum(1 for t in self.trades if t.pnl > 0)
        return winning_trades / len(self.trades)

    def profit_factor(self) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        gross_profit = sum(t.pnl for t in self.trades if t.pnl > 0)
        gross_loss = abs(sum(t.pnl for t in self.trades if t.pnl < 0))

        if gross_loss == 0:
            return float('inf')

        return gross_profit / gross_loss
```

### Metric Interpretation

**Sharpe Ratio:**
- <0.5: Poor
- 0.5-1.0: Acceptable
- 1.0-2.0: Good
- 2.0-3.0: Very good
- >3.0: Excellent (verify not overfit)

**Max Drawdown:**
- <10%: Conservative
- 10-20%: Moderate
- 20-30%: Aggressive
- >30%: Very aggressive (difficult to stomach)

**Win Rate:**
- Momentum: 40-60% typical
- Mean Reversion: 60-75% typical
- Arbitrage: 90%+ expected

## Validation Techniques

### 1. Walk-Forward Optimization

```python
def walk_forward_optimization(
    data: pd.DataFrame,
    strategy_class: type,
    param_ranges: dict,
    train_period: int = 90,  # days
    test_period: int = 30  # days
) -> pd.DataFrame:
    """Walk-forward optimization"""

    results = []

    # Generate rolling windows
    total_days = len(data)
    window_size = train_period + test_period

    for start_idx in range(0, total_days - window_size, test_period):
        # Split into train and test
        train_data = data.iloc[start_idx:start_idx + train_period]
        test_data = data.iloc[start_idx + train_period:start_idx + window_size]

        # Optimize on training data
        best_params = optimize_parameters(
            strategy_class,
            train_data,
            param_ranges
        )

        # Test on out-of-sample data
        strategy = strategy_class(**best_params)
        test_result = backtest(strategy, test_data)

        results.append({
            'start_date': test_data.index[0],
            'end_date': test_data.index[-1],
            'params': best_params,
            'return': test_result.total_return,
            'sharpe': test_result.sharpe_ratio,
            'num_trades': test_result.num_trades
        })

    return pd.DataFrame(results)
```

### 2. Monte Carlo Simulation

```python
def monte_carlo_simulation(
    trades: List[Trade],
    num_simulations: int = 1000
) -> Dict:
    """Monte Carlo simulation for confidence intervals"""

    trade_returns = [t.pnl / t.entry_value for t in trades]

    simulated_results = []

    for _ in range(num_simulations):
        # Randomly shuffle trades (bootstrap)
        shuffled = np.random.choice(trade_returns, size=len(trade_returns))

        # Calculate cumulative return
        cumulative = (1 + pd.Series(shuffled)).cumprod().iloc[-1] - 1
        simulated_results.append(cumulative)

    simulated_results = sorted(simulated_results)

    return {
        'median_return': np.median(simulated_results),
        '5th_percentile': simulated_results[int(len(simulated_results) * 0.05)],
        '95th_percentile': simulated_results[int(len(simulated_results) * 0.95)],
        'worst_case': min(simulated_results),
        'best_case': max(simulated_results)
    }
```

### 3. Robustness Testing

```python
def test_parameter_robustness(
    strategy_class: type,
    data: pd.DataFrame,
    base_params: dict,
    sensitivity_pct: float = 0.20  # ±20%
) -> pd.DataFrame:
    """Test how sensitive strategy is to parameter changes"""

    results = []

    for param_name, base_value in base_params.items():
        # Test ±20% variations
        test_values = [
            base_value * (1 - sensitivity_pct),
            base_value,
            base_value * (1 + sensitivity_pct)
        ]

        for test_value in test_values:
            params = base_params.copy()
            params[param_name] = test_value

            strategy = strategy_class(**params)
            result = backtest(strategy, data)

            results.append({
                'parameter': param_name,
                'value': test_value,
                'value_change_pct': (test_value / base_value - 1) * 100,
                'sharpe_ratio': result.sharpe_ratio,
                'total_return': result.total_return
            })

    return pd.DataFrame(results)
```

## Checklist

Before trusting backtest results, verify:

- [ ] Data quality validated (no missing/anomalous data)
- [ ] Look-ahead bias prevented (point-in-time data only)
- [ ] Survivor bias avoided (historical universe)
- [ ] Realistic fees included (maker/taker, VIP tiers)
- [ ] Slippage modeled (based on volume and liquidity)
- [ ] Execution delays simulated (latency, fills)
- [ ] Minimum 100 trades executed
- [ ] Out-of-sample testing performed
- [ ] Parameter robustness verified
- [ ] Performance metrics calculated correctly
- [ ] Results compared to buy-and-hold benchmark
- [ ] Maximum drawdown acceptable for risk tolerance

## Conclusion

Accurate backtesting requires meticulous attention to detail and realistic assumptions. The difference between backtest returns and live trading returns is often 50%+ due to execution costs, slippage, and unrealistic assumptions.

**Key Principle:** If backtest results seem too good to be true, they probably are. Always err on the side of conservative assumptions.
