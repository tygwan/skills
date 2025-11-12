#!/usr/bin/env python3
"""
Real-time Liquidation Monitoring Daemon
Monitors leveraged positions and alerts on critical risk levels.
"""

import asyncio
import json
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from risk_calculator import LeveragedPosition, LiquidationCalculator


class LiquidationRisk(Enum):
    SAFE = "safe"  # >20% from liquidation
    WARNING = "warning"  # 10-20% from liquidation
    DANGER = "danger"  # 5-10% from liquidation
    CRITICAL = "critical"  # <5% from liquidation


class LiquidationMonitor:
    """Real-time liquidation risk monitoring"""

    def __init__(
        self,
        positions: List[LeveragedPosition],
        check_interval_seconds: int = 30,
        alert_callback=None
    ):
        self.positions = {pos.symbol: pos for pos in positions}
        self.check_interval = check_interval_seconds
        self.alert_callback = alert_callback or self._default_alert
        self.risk_history: Dict[str, List[dict]] = {}

    def add_position(self, position: LeveragedPosition):
        """Add new position to monitor"""
        self.positions[position.symbol] = position
        self.risk_history[position.symbol] = []

    def remove_position(self, symbol: str):
        """Remove position from monitoring"""
        if symbol in self.positions:
            del self.positions[symbol]

    def assess_risk(self, symbol: str, current_price: float) -> dict:
        """Assess liquidation risk for a position"""
        if symbol not in self.positions:
            return {"error": "Position not found"}

        position = self.positions[symbol]
        liq_price = LiquidationCalculator.calculate_liquidation_price(position)
        distance_pct = LiquidationCalculator.get_distance_to_liquidation(
            position, current_price
        )

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
            "symbol": symbol,
            "risk_level": risk.value,
            "liquidation_price": liq_price,
            "current_price": current_price,
            "distance_pct": distance_pct,
            "recommended_action": action,
            "timestamp": datetime.now().isoformat()
        }

    async def monitor_position(self, symbol: str, price_fetcher):
        """Monitor single position continuously"""
        while symbol in self.positions:
            try:
                current_price = await price_fetcher(symbol)
                risk = self.assess_risk(symbol, current_price)

                # Store in history
                if symbol not in self.risk_history:
                    self.risk_history[symbol] = []
                self.risk_history[symbol].append(risk)

                # Keep only last 100 records
                if len(self.risk_history[symbol]) > 100:
                    self.risk_history[symbol] = self.risk_history[symbol][-100:]

                # Alert on dangerous conditions
                if risk["risk_level"] in ["danger", "critical"]:
                    await self.alert_callback(risk)

            except Exception as e:
                print(f"Error monitoring {symbol}: {e}")

            await asyncio.sleep(self.check_interval)

    async def monitor_all(self, price_fetcher):
        """Monitor all positions concurrently"""
        tasks = [
            self.monitor_position(symbol, price_fetcher)
            for symbol in self.positions.keys()
        ]
        await asyncio.gather(*tasks)

    async def _default_alert(self, risk: dict):
        """Default alert handler"""
        print(f"\n🚨 LIQUIDATION RISK ALERT 🚨")
        print(f"Symbol: {risk['symbol']}")
        print(f"Risk Level: {risk['risk_level'].upper()}")
        print(f"Current Price: ${risk['current_price']:.2f}")
        print(f"Liquidation Price: ${risk['liquidation_price']:.2f}")
        print(f"Distance: {risk['distance_pct']:.2f}%")
        print(f"Action: {risk['recommended_action']}")
        print(f"Time: {risk['timestamp']}")

    def get_risk_summary(self) -> dict:
        """Get summary of all positions"""
        summary = {
            "total_positions": len(self.positions),
            "by_risk_level": {
                "safe": 0,
                "warning": 0,
                "danger": 0,
                "critical": 0
            },
            "positions": []
        }

        for symbol, history in self.risk_history.items():
            if history:
                latest = history[-1]
                summary["by_risk_level"][latest["risk_level"]] += 1
                summary["positions"].append({
                    "symbol": symbol,
                    "risk_level": latest["risk_level"],
                    "distance_pct": latest["distance_pct"],
                    "last_check": latest["timestamp"]
                })

        return summary


# Example price fetcher (replace with actual exchange API)
async def mock_price_fetcher(symbol: str) -> float:
    """Mock price fetcher for testing"""
    # Simulate price fluctuation
    import random
    base_prices = {
        "BTCUSDT": 50000.0,
        "ETHUSDT": 3000.0
    }
    base = base_prices.get(symbol, 1000.0)
    return base * random.uniform(0.95, 1.05)


async def main():
    """Example usage"""
    positions = [
        LeveragedPosition(
            symbol="BTCUSDT",
            side="LONG",
            entry_price=50000.0,
            position_size=1.0,
            leverage=10.0,
            initial_margin=5000.0
        ),
        LeveragedPosition(
            symbol="ETHUSDT",
            side="LONG",
            entry_price=3000.0,
            position_size=10.0,
            leverage=5.0,
            initial_margin=6000.0
        )
    ]

    monitor = LiquidationMonitor(
        positions=positions,
        check_interval_seconds=5  # Check every 5 seconds for demo
    )

    print("Starting liquidation monitor...")
    print("Press Ctrl+C to stop\n")

    try:
        # Run for 60 seconds as demo
        await asyncio.wait_for(
            monitor.monitor_all(mock_price_fetcher),
            timeout=60.0
        )
    except asyncio.TimeoutError:
        print("\n\nMonitoring session ended.")
        summary = monitor.get_risk_summary()
        print("\n=== Risk Summary ===")
        print(json.dumps(summary, indent=2))
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")


if __name__ == "__main__":
    asyncio.run(main())
