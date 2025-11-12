#!/usr/bin/env python3
"""
Crypto Risk Management Calculator
All-in-one risk calculation utilities for crypto trading.
"""

from dataclasses import dataclass
from datetime import datetime
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


@dataclass
class LeveragedPosition:
    """Leveraged trading position"""
    symbol: str
    side: str  # "LONG" or "SHORT"
    entry_price: float
    position_size: float  # in base asset
    leverage: float
    initial_margin: float
    maintenance_margin_rate: float = 0.005  # 0.5% for most exchanges


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


class LiquidationCalculator:
    """Calculate liquidation prices and risk levels"""

    @staticmethod
    def calculate_liquidation_price(position: LeveragedPosition) -> float:
        """Calculate exact liquidation price"""
        margin_ratio = position.initial_margin / position.leverage

        if position.side == "LONG":
            return position.entry_price * (1 - margin_ratio)
        else:  # SHORT
            return position.entry_price * (1 + margin_ratio)

    @staticmethod
    def get_distance_to_liquidation(
        position: LeveragedPosition,
        current_price: float
    ) -> float:
        """Calculate percentage distance to liquidation"""
        liq_price = LiquidationCalculator.calculate_liquidation_price(position)

        if position.side == "LONG":
            distance_pct = ((current_price - liq_price) / current_price) * 100
        else:  # SHORT
            distance_pct = ((liq_price - current_price) / current_price) * 100

        return distance_pct


class SlippageCalculator:
    """Calculate slippage for CEX and DEX trades"""

    @staticmethod
    def calculate_slippage(expected_price: float, executed_price: float) -> float:
        """Calculate actual slippage percentage"""
        slippage_pct = abs(
            (executed_price - expected_price) / expected_price
        ) * 100
        return slippage_pct

    @staticmethod
    def get_price_limits(
        side: str,
        market_price: float,
        slippage_tolerance_pct: float = 0.5
    ) -> dict:
        """Calculate min/max acceptable execution prices"""
        tolerance_decimal = slippage_tolerance_pct / 100

        if side == "BUY":
            max_price = market_price * (1 + tolerance_decimal)
            return {
                "side": "BUY",
                "market_price": market_price,
                "max_acceptable_price": max_price,
                "slippage_tolerance_pct": slippage_tolerance_pct
            }
        else:  # SELL
            min_price = market_price * (1 - tolerance_decimal)
            return {
                "side": "SELL",
                "market_price": market_price,
                "min_acceptable_price": min_price,
                "slippage_tolerance_pct": slippage_tolerance_pct
            }

    @staticmethod
    def estimate_dex_slippage(
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
            "total_slippage_pct": total_slippage
        }


class DrawdownCalculator:
    """Calculate portfolio drawdown metrics"""

    @staticmethod
    def calculate_drawdown(peak_value: float, current_value: float) -> float:
        """Calculate drawdown percentage"""
        if peak_value == 0:
            return 0.0
        return ((peak_value - current_value) / peak_value) * 100

    @staticmethod
    def get_risk_status(
        drawdown_pct: float,
        max_drawdown_pct: float = 20.0
    ) -> dict:
        """Get current drawdown risk status"""
        if drawdown_pct < max_drawdown_pct * 0.5:
            status = "healthy"
            action = "continue_trading"
        elif drawdown_pct < max_drawdown_pct * 0.75:
            status = "warning"
            action = "reduce_position_sizes_25pct"
        elif drawdown_pct < max_drawdown_pct:
            status = "danger"
            action = "reduce_position_sizes_50pct"
        else:
            status = "limit_exceeded"
            action = "halt_all_trading"

        return {
            "status": status,
            "drawdown_pct": drawdown_pct,
            "max_allowed_pct": max_drawdown_pct,
            "remaining_buffer_pct": max_drawdown_pct - drawdown_pct,
            "recommended_action": action
        }


def main():
    """Example usage of risk calculators"""

    # Kelly Position Sizing
    print("=== Kelly Position Sizing ===")
    metrics = TradingMetrics(
        total_trades=100,
        wins=60,
        losses=40,
        avg_win=0.08,
        avg_loss=-0.05,
        portfolio_value=100000.0
    )

    sizer = KellyPositionSizer(metrics, fractional_kelly=0.25)
    position = sizer.get_position_size(signal_confidence=0.9)
    print(f"Position size: ${position['position_usd']:.2f} ({position['final_position_pct']*100:.2f}%)")
    print(f"Max loss: ${position['max_loss_usd']:.2f}")

    # Liquidation Risk
    print("\n=== Liquidation Risk ===")
    lev_position = LeveragedPosition(
        symbol="BTCUSDT",
        side="LONG",
        entry_price=50000.0,
        position_size=1.0,
        leverage=10.0,
        initial_margin=5000.0
    )

    liq_price = LiquidationCalculator.calculate_liquidation_price(lev_position)
    distance = LiquidationCalculator.get_distance_to_liquidation(lev_position, 48000.0)
    print(f"Liquidation price: ${liq_price:.2f}")
    print(f"Distance to liquidation: {distance:.2f}%")

    # Slippage
    print("\n=== Slippage ===")
    limits = SlippageCalculator.get_price_limits("BUY", 50000.0, 0.5)
    print(f"Max buy price (0.5% slippage): ${limits['max_acceptable_price']:.2f}")

    dex_slippage = SlippageCalculator.estimate_dex_slippage(10000.0, 1000000.0)
    print(f"DEX slippage estimate: {dex_slippage['total_slippage_pct']:.2f}%")

    # Drawdown
    print("\n=== Drawdown ===")
    drawdown = DrawdownCalculator.calculate_drawdown(100000.0, 85000.0)
    status = DrawdownCalculator.get_risk_status(drawdown)
    print(f"Current drawdown: {status['drawdown_pct']:.2f}%")
    print(f"Status: {status['status']}")
    print(f"Action: {status['recommended_action']}")


if __name__ == "__main__":
    main()
