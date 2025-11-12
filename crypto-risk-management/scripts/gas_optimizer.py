#!/usr/bin/env python3
"""
Gas Optimization for Ethereum Transactions
Fetches real-time gas prices and makes execution decisions.
"""

import asyncio
import json
from datetime import datetime
from typing import Optional
from web3 import Web3


class GasOptimizer:
    """Optimize gas costs for Ethereum transactions"""

    def __init__(self, rpc_url: str, network: str = "mainnet"):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.network = network
        self.base_gas_limit = {
            "simple_transfer": 21000,
            "erc20_transfer": 65000,
            "erc20_approve": 45000,
            "uniswap_v2_swap": 150000,
            "uniswap_v3_swap": 180000,
            "aave_deposit": 250000,
            "aave_borrow": 300000,
            "complex_defi": 400000
        }

    def get_current_gas_prices(self) -> dict:
        """Get current gas prices in Gwei"""
        try:
            latest_block = self.w3.eth.get_block('latest')
            base_fee = latest_block.get('baseFeePerGas', 0)

            # Priority fees for different speeds (EIP-1559)
            priority_fees = {
                "slow": self.w3.to_wei(1, 'gwei'),     # ~5 min
                "medium": self.w3.to_wei(1.5, 'gwei'), # ~2 min
                "fast": self.w3.to_wei(2, 'gwei'),     # ~30 sec
                "instant": self.w3.to_wei(3, 'gwei')   # Next block
            }

            gas_prices = {}
            for speed, priority in priority_fees.items():
                max_fee = base_fee + priority
                gas_prices[speed] = {
                    "max_fee_per_gas": max_fee,
                    "max_priority_fee_per_gas": priority,
                    "max_fee_gwei": float(self.w3.from_wei(max_fee, 'gwei')),
                    "base_fee_gwei": float(self.w3.from_wei(base_fee, 'gwei')),
                    "priority_fee_gwei": float(self.w3.from_wei(priority, 'gwei'))
                }

            return {
                "timestamp": datetime.now().isoformat(),
                "block_number": latest_block['number'],
                "gas_prices": gas_prices
            }

        except Exception as e:
            # Fallback to legacy gas price
            try:
                legacy_price = self.w3.eth.gas_price
                return {
                    "timestamp": datetime.now().isoformat(),
                    "legacy": True,
                    "gas_price": legacy_price,
                    "gas_price_gwei": float(self.w3.from_wei(legacy_price, 'gwei'))
                }
            except Exception as inner_e:
                return {
                    "error": f"Failed to fetch gas prices: {str(e)}, {str(inner_e)}",
                    "timestamp": datetime.now().isoformat()
                }

    def estimate_transaction_cost(
        self,
        tx_type: str,
        speed: str = "medium",
        eth_price_usd: Optional[float] = None,
        custom_gas_limit: Optional[int] = None
    ) -> dict:
        """Estimate total transaction cost"""
        gas_data = self.get_current_gas_prices()

        if "error" in gas_data:
            return gas_data

        gas_limit = custom_gas_limit or self.base_gas_limit.get(tx_type, 100000)

        if "gas_prices" in gas_data:
            # EIP-1559 pricing
            if speed not in gas_data["gas_prices"]:
                speed = "medium"

            price_info = gas_data["gas_prices"][speed]
            max_fee = price_info["max_fee_per_gas"]
            max_cost_wei = gas_limit * max_fee
            max_cost_eth = float(self.w3.from_wei(max_cost_wei, 'ether'))

            result = {
                "tx_type": tx_type,
                "gas_limit": gas_limit,
                "speed": speed,
                "max_fee_gwei": price_info["max_fee_gwei"],
                "base_fee_gwei": price_info["base_fee_gwei"],
                "priority_fee_gwei": price_info["priority_fee_gwei"],
                "max_cost_eth": max_cost_eth,
                "block_number": gas_data["block_number"],
                "timestamp": gas_data["timestamp"]
            }

            if eth_price_usd:
                result["max_cost_usd"] = max_cost_eth * eth_price_usd
                result["eth_price_usd"] = eth_price_usd

            return result

        else:
            # Legacy pricing
            legacy_price = gas_data["gas_price"]
            cost_wei = gas_limit * legacy_price
            cost_eth = float(self.w3.from_wei(cost_wei, 'ether'))

            result = {
                "tx_type": tx_type,
                "gas_limit": gas_limit,
                "gas_price_gwei": gas_data["gas_price_gwei"],
                "cost_eth": cost_eth,
                "legacy": True,
                "timestamp": gas_data["timestamp"]
            }

            if eth_price_usd:
                result["cost_usd"] = cost_eth * eth_price_usd
                result["eth_price_usd"] = eth_price_usd

            return result

    def should_execute_transaction(
        self,
        tx_type: str,
        expected_profit_usd: float,
        eth_price_usd: float,
        min_profit_ratio: float = 2.0,
        speed: str = "medium"
    ) -> dict:
        """Determine if transaction is worth executing based on gas costs"""
        cost = self.estimate_transaction_cost(tx_type, speed, eth_price_usd)

        if "error" in cost:
            return {
                "error": cost["error"],
                "should_execute": False
            }

        gas_cost_usd = cost.get("max_cost_usd") or cost.get("cost_usd", 0)
        net_profit = expected_profit_usd - gas_cost_usd
        profit_ratio = expected_profit_usd / gas_cost_usd if gas_cost_usd > 0 else float('inf')

        should_execute = profit_ratio >= min_profit_ratio and net_profit > 0

        return {
            "should_execute": should_execute,
            "expected_profit_usd": expected_profit_usd,
            "gas_cost_usd": gas_cost_usd,
            "net_profit_usd": net_profit,
            "profit_ratio": profit_ratio,
            "min_profit_ratio": min_profit_ratio,
            "reason": "Profitable" if should_execute else "Gas costs too high",
            "gas_details": cost
        }

    def find_optimal_timing(
        self,
        tx_type: str,
        target_gas_gwei: float,
        timeout_minutes: int = 60
    ) -> dict:
        """Monitor gas prices and recommend optimal execution time"""
        # This would typically run in a loop monitoring gas prices
        current = self.get_current_gas_prices()

        if "error" in current:
            return current

        if "gas_prices" in current:
            medium_price = current["gas_prices"]["medium"]["max_fee_gwei"]

            if medium_price <= target_gas_gwei:
                return {
                    "execute_now": True,
                    "current_gas_gwei": medium_price,
                    "target_gas_gwei": target_gas_gwei,
                    "savings_pct": ((target_gas_gwei - medium_price) / target_gas_gwei) * 100,
                    "timestamp": current["timestamp"]
                }
            else:
                return {
                    "execute_now": False,
                    "current_gas_gwei": medium_price,
                    "target_gas_gwei": target_gas_gwei,
                    "wait_for_lower": True,
                    "premium_pct": ((medium_price - target_gas_gwei) / target_gas_gwei) * 100,
                    "timestamp": current["timestamp"]
                }
        else:
            # Legacy pricing
            current_gwei = current["gas_price_gwei"]
            return {
                "execute_now": current_gwei <= target_gas_gwei,
                "current_gas_gwei": current_gwei,
                "target_gas_gwei": target_gas_gwei,
                "legacy": True,
                "timestamp": current["timestamp"]
            }


async def monitor_gas_prices(optimizer: GasOptimizer, interval_seconds: int = 60):
    """Monitor gas prices continuously"""
    print("Starting gas price monitoring...")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            prices = optimizer.get_current_gas_prices()

            if "gas_prices" in prices:
                print(f"\n[{prices['timestamp']}] Block: {prices['block_number']}")
                print(f"Base Fee: {prices['gas_prices']['medium']['base_fee_gwei']:.2f} Gwei")
                print(f"Slow:    {prices['gas_prices']['slow']['max_fee_gwei']:.2f} Gwei")
                print(f"Medium:  {prices['gas_prices']['medium']['max_fee_gwei']:.2f} Gwei")
                print(f"Fast:    {prices['gas_prices']['fast']['max_fee_gwei']:.2f} Gwei")
                print(f"Instant: {prices['gas_prices']['instant']['max_fee_gwei']:.2f} Gwei")
            elif "gas_price_gwei" in prices:
                print(f"\n[{prices['timestamp']}] Gas Price: {prices['gas_price_gwei']:.2f} Gwei (Legacy)")
            else:
                print(f"\n[{prices['timestamp']}] Error: {prices.get('error', 'Unknown')}")

            await asyncio.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")


def main():
    """Example usage"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python gas_optimizer.py <RPC_URL> [eth_price_usd]")
        print("\nExample:")
        print("  python gas_optimizer.py https://mainnet.infura.io/v3/YOUR_KEY 3000")
        sys.exit(1)

    rpc_url = sys.argv[1]
    eth_price = float(sys.argv[2]) if len(sys.argv) > 2 else None

    optimizer = GasOptimizer(rpc_url)

    print("=== Current Gas Prices ===")
    prices = optimizer.get_current_gas_prices()
    print(json.dumps(prices, indent=2))

    if eth_price:
        print(f"\n=== Transaction Cost Estimates (ETH @ ${eth_price}) ===")

        tx_types = [
            "simple_transfer",
            "erc20_transfer",
            "uniswap_v2_swap",
            "aave_deposit"
        ]

        for tx_type in tx_types:
            cost = optimizer.estimate_transaction_cost(tx_type, "medium", eth_price)
            if "max_cost_usd" in cost:
                print(f"\n{tx_type}:")
                print(f"  Gas Limit: {cost['gas_limit']}")
                print(f"  Max Fee: {cost['max_fee_gwei']:.2f} Gwei")
                print(f"  Max Cost: ${cost['max_cost_usd']:.2f}")

        print("\n=== Should Execute? ===")
        decision = optimizer.should_execute_transaction(
            tx_type="uniswap_v2_swap",
            expected_profit_usd=50.0,
            eth_price_usd=eth_price,
            min_profit_ratio=2.0
        )
        print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    if "--monitor" in sys.argv:
        import sys
        rpc_url = sys.argv[1] if len(sys.argv) > 1 else "https://mainnet.infura.io/v3/YOUR_KEY"
        optimizer = GasOptimizer(rpc_url)
        asyncio.run(monitor_gas_prices(optimizer, interval_seconds=30))
    else:
        main()
