# DeFi Protocol Integration Guide

Guide for integrating decentralized finance (DeFi) protocols into crypto trading agents.

## Overview

DeFi protocols enable permissionless trading and financial operations on blockchain:

- **Uniswap/Sushiswap:** Automated market makers (AMM) for token swaps
- **Aave/Compound:** Lending and borrowing protocols
- **dYdX:** Decentralized perpetual futures exchange
- **Curve:** Stablecoin and low-slippage swaps
- **1inch/Matcha:** DEX aggregators for best execution

## Uniswap V3 Integration

### Setup

```bash
npm install @uniswap/v3-sdk @uniswap/sdk-core ethers
```

### Swap Tokens

```python
from web3 import Web3
from eth_account import Account
import json

class UniswapV3Adapter:
    """Uniswap V3 integration for token swaps."""

    def __init__(
        self,
        web3_provider: str,
        router_address: str,
        private_key: str
    ):
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        self.router_address = router_address
        self.account = Account.from_key(private_key)

        # Load router ABI
        with open('uniswap_v3_router_abi.json') as f:
            self.router_abi = json.load(f)

        self.router = self.w3.eth.contract(
            address=router_address,
            abi=self.router_abi
        )

    def swap_exact_tokens(
        self,
        token_in: str,
        token_out: str,
        amount_in: int,
        min_amount_out: int,
        fee: int = 3000,  # 0.3% fee tier
        slippage: float = 0.01  # 1% slippage
    ):
        """Swap exact amount of input tokens."""

        # Encode swap path (token_in -> fee -> token_out)
        path = self._encode_path([token_in, token_out], [fee])

        # Calculate minimum output with slippage
        min_out = int(min_amount_out * (1 - slippage))

        # Build transaction
        swap_params = {
            'path': path,
            'recipient': self.account.address,
            'deadline': int(time.time() + 300),  # 5 min deadline
            'amountIn': amount_in,
            'amountOutMinimum': min_out
        }

        # Estimate gas
        gas_estimate = self.router.functions.exactInput(
            swap_params
        ).estimate_gas({'from': self.account.address})

        # Build and sign transaction
        transaction = self.router.functions.exactInput(
            swap_params
        ).build_transaction({
            'from': self.account.address,
            'gas': int(gas_estimate * 1.2),  # 20% buffer
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address)
        })

        signed_txn = self.account.sign_transaction(transaction)

        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        return tx_hash.hex()

    def _encode_path(self, tokens: list[str], fees: list[int]) -> bytes:
        """Encode Uniswap V3 swap path."""
        # Format: token0 + fee0 + token1 + fee1 + token2 ...
        path = tokens[0]

        for i, fee in enumerate(fees):
            path += fee.to_bytes(3, 'big')
            path += tokens[i + 1]

        return path
```

### Get Quote

```python
class UniswapQuoter:
    """Get price quotes from Uniswap."""

    def __init__(self, quoter_address: str, web3_provider: str):
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        self.quoter = self.w3.eth.contract(
            address=quoter_address,
            abi=quoter_abi
        )

    def quote_exact_input(
        self,
        token_in: str,
        token_out: str,
        amount_in: int,
        fee: int = 3000
    ) -> tuple[int, int]:
        """Get quote for exact input swap."""

        path = self._encode_path([token_in, token_out], [fee])

        result = self.quoter.functions.quoteExactInput(
            path,
            amount_in
        ).call()

        amount_out = result[0]
        gas_estimate = result[1]

        return amount_out, gas_estimate
```

### Liquidity Provision

```python
class UniswapLiquidityProvider:
    """Provide liquidity to Uniswap V3 pools."""

    def add_liquidity(
        self,
        token0: str,
        token1: str,
        fee: int,
        amount0: int,
        amount1: int,
        tick_lower: int,
        tick_upper: int
    ):
        """Add liquidity to pool."""

        # Approve tokens
        self._approve_token(token0, amount0)
        self._approve_token(token1, amount1)

        # Calculate price range
        sqrt_price_lower = self._tick_to_sqrt_price(tick_lower)
        sqrt_price_upper = self._tick_to_sqrt_price(tick_upper)

        # Add liquidity
        params = {
            'token0': token0,
            'token1': token1,
            'fee': fee,
            'tickLower': tick_lower,
            'tickUpper': tick_upper,
            'amount0Desired': amount0,
            'amount1Desired': amount1,
            'amount0Min': int(amount0 * 0.99),  # 1% slippage
            'amount1Min': int(amount1 * 0.99),
            'recipient': self.account.address,
            'deadline': int(time.time() + 300)
        }

        tx = self.position_manager.functions.mint(params).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address)
        })

        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return tx_hash.hex()
```

## Aave Integration

### Lending

```python
class AaveAdapter:
    """Aave lending protocol integration."""

    def __init__(self, lending_pool_address: str, web3_provider: str):
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        self.lending_pool = self.w3.eth.contract(
            address=lending_pool_address,
            abi=aave_lending_pool_abi
        )

    def deposit(
        self,
        asset: str,
        amount: int,
        on_behalf_of: str = None
    ):
        """Deposit asset to Aave."""

        if on_behalf_of is None:
            on_behalf_of = self.account.address

        # Approve asset
        self._approve_token(asset, amount)

        # Deposit
        tx = self.lending_pool.functions.deposit(
            asset,
            amount,
            on_behalf_of,
            0  # referral code
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address)
        })

        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return tx_hash.hex()

    def withdraw(self, asset: str, amount: int):
        """Withdraw asset from Aave."""

        # amount = -1 means withdraw all
        tx = self.lending_pool.functions.withdraw(
            asset,
            amount,
            self.account.address
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address)
        })

        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return tx_hash.hex()

    def borrow(
        self,
        asset: str,
        amount: int,
        interest_rate_mode: int = 2  # 1 = stable, 2 = variable
    ):
        """Borrow asset from Aave."""

        tx = self.lending_pool.functions.borrow(
            asset,
            amount,
            interest_rate_mode,
            0,  # referral code
            self.account.address
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address)
        })

        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return tx_hash.hex()

    def get_user_account_data(self, user: str) -> dict:
        """Get user's account data."""

        data = self.lending_pool.functions.getUserAccountData(user).call()

        return {
            'total_collateral_eth': data[0],
            'total_debt_eth': data[1],
            'available_borrow_eth': data[2],
            'liquidation_threshold': data[3],
            'ltv': data[4],
            'health_factor': data[5] / 1e18  # Normalize
        }
```

### Health Factor Monitoring

```python
class AaveHealthMonitor:
    """Monitor Aave position health factor."""

    def __init__(self, aave_adapter: AaveAdapter):
        self.aave = aave_adapter
        self.min_health_factor = 1.5  # Min 1.5 to avoid liquidation

    def check_health(self, user: str) -> bool:
        """Check if position is healthy."""

        data = self.aave.get_user_account_data(user)
        health_factor = data['health_factor']

        if health_factor < self.min_health_factor:
            logger.warning(
                f"Health factor {health_factor:.2f} below minimum {self.min_health_factor}"
            )
            return False

        return True

    def calculate_max_borrow(self, user: str) -> float:
        """Calculate maximum safe borrow amount."""

        data = self.aave.get_user_account_data(user)

        # Borrow up to 80% of available to maintain health factor
        max_borrow = data['available_borrow_eth'] * 0.8

        return max_borrow
```

## dYdX Integration

### Perpetual Futures Trading

```python
from dydx3 import Client
from dydx3.constants import *

class DydxAdapter:
    """dYdX perpetual futures trading."""

    def __init__(
        self,
        ethereum_address: str,
        private_key: str,
        network: str = NETWORK_ID_MAINNET
    ):
        self.client = Client(
            host=API_HOST_MAINNET if network == NETWORK_ID_MAINNET else API_HOST_ROPSTEN,
            default_ethereum_address=ethereum_address,
            eth_private_key=private_key,
            network_id=network
        )

        # Get account
        self.account = self.client.private.get_account()
        self.position_id = self.account.data['account']['positionId']

    def place_order(
        self,
        market: str,
        side: str,  # BUY or SELL
        order_type: str,  # MARKET or LIMIT
        size: float,
        price: float = None,
        leverage: int = 3
    ):
        """Place perpetual futures order."""

        # Create order
        order_params = {
            'position_id': self.position_id,
            'market': market,
            'side': ORDER_SIDE_BUY if side == "BUY" else ORDER_SIDE_SELL,
            'order_type': ORDER_TYPE_MARKET if order_type == "MARKET" else ORDER_TYPE_LIMIT,
            'post_only': False,
            'size': str(size),
            'expiration_epoch_seconds': int(time.time() + 86400),  # 24h
            'time_in_force': TIME_IN_FORCE_FOK
        }

        if order_type == "LIMIT":
            order_params['price'] = str(price)

        order = self.client.private.create_order(**order_params)

        return order.data

    def get_positions(self) -> list:
        """Get open positions."""

        positions = self.client.private.get_positions(
            market=MARKET_BTC_USD,
            status=POSITION_STATUS_OPEN
        )

        return positions.data['positions']

    def close_position(self, market: str):
        """Close position."""

        positions = self.get_positions()

        for pos in positions:
            if pos['market'] == market:
                # Close by placing opposite order
                side = "SELL" if pos['side'] == 'LONG' else "BUY"
                size = abs(float(pos['size']))

                return self.place_order(
                    market=market,
                    side=side,
                    order_type="MARKET",
                    size=size
                )
```

## DEX Aggregators (1inch)

### Best Execution

```python
class OneInchAggregator:
    """1inch DEX aggregator for best execution."""

    def __init__(self, api_key: str, chain_id: int = 1):
        self.api_key = api_key
        self.chain_id = chain_id
        self.base_url = f"https://api.1inch.io/v5.0/{chain_id}"

    def get_quote(
        self,
        from_token: str,
        to_token: str,
        amount: int
    ) -> dict:
        """Get quote from 1inch."""

        url = f"{self.base_url}/quote"

        params = {
            'fromTokenAddress': from_token,
            'toTokenAddress': to_token,
            'amount': amount
        }

        headers = {'Authorization': f'Bearer {self.api_key}'}

        response = requests.get(url, params=params, headers=headers)
        return response.json()

    def execute_swap(
        self,
        from_token: str,
        to_token: str,
        amount: int,
        slippage: float = 1.0,  # 1%
        from_address: str = None
    ):
        """Execute swap via 1inch."""

        if from_address is None:
            from_address = self.account.address

        url = f"{self.base_url}/swap"

        params = {
            'fromTokenAddress': from_token,
            'toTokenAddress': to_token,
            'amount': amount,
            'fromAddress': from_address,
            'slippage': slippage
        }

        headers = {'Authorization': f'Bearer {self.api_key}'}

        response = requests.get(url, params=params, headers=headers)
        swap_data = response.json()

        # Execute transaction
        tx = swap_data['tx']
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return tx_hash.hex()
```

## Gas Optimization

### Gas Price Strategies

```python
class GasOptimizer:
    """Optimize gas costs for DeFi transactions."""

    def __init__(self, w3: Web3):
        self.w3 = w3

    def get_optimal_gas_price(self, priority: str = "standard") -> int:
        """Get optimal gas price based on priority."""

        # Get EIP-1559 fees
        latest_block = self.w3.eth.get_block('latest')
        base_fee = latest_block['baseFeePerGas']

        # Priority fee based on urgency
        priority_fees = {
            'low': int(base_fee * 0.1),      # 10% tip
            'standard': int(base_fee * 0.3),  # 30% tip
            'high': int(base_fee * 0.5),     # 50% tip
            'urgent': int(base_fee * 1.0)    # 100% tip
        }

        max_priority_fee = priority_fees[priority]
        max_fee = base_fee + max_priority_fee

        return {
            'maxFeePerGas': max_fee,
            'maxPriorityFeePerGas': max_priority_fee
        }

    def estimate_gas_cost(
        self,
        transaction: dict,
        gas_price: int = None
    ) -> float:
        """Estimate gas cost in ETH."""

        if gas_price is None:
            gas_price = self.get_optimal_gas_price()['maxFeePerGas']

        gas_limit = self.w3.eth.estimate_gas(transaction)

        # Cost in wei
        gas_cost_wei = gas_limit * gas_price

        # Convert to ETH
        gas_cost_eth = self.w3.from_wei(gas_cost_wei, 'ether')

        return float(gas_cost_eth)
```

## Testing DeFi Integration

### Fork Mainnet for Testing

```python
import pytest
from eth_tester import EthereumTester
from web3 import Web3, EthereumTesterProvider

@pytest.fixture
def forked_mainnet():
    """Fork mainnet for testing."""

    # Use Hardhat or Ganache to fork mainnet
    fork_url = "http://localhost:8545"

    w3 = Web3(Web3.HTTPProvider(fork_url))

    # Set up test account with ETH
    test_account = w3.eth.accounts[0]

    return w3, test_account

@pytest.mark.integration
async def test_uniswap_swap_on_fork(forked_mainnet):
    """Test Uniswap swap on forked mainnet."""

    w3, account = forked_mainnet

    # Initialize Uniswap adapter
    uniswap = UniswapV3Adapter(
        web3_provider="http://localhost:8545",
        router_address=UNISWAP_V3_ROUTER,
        private_key=test_private_key
    )

    # Execute swap
    tx_hash = uniswap.swap_exact_tokens(
        token_in=WETH_ADDRESS,
        token_out=USDC_ADDRESS,
        amount_in=w3.to_wei(1, 'ether'),
        min_amount_out=3000 * 10**6  # 3000 USDC
    )

    # Wait for transaction
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    assert receipt['status'] == 1  # Success
```

## Best Practices

1. **Use Testnet/Forked Mainnet:** Never test on mainnet with real funds
2. **Set Slippage Limits:** Protect against MEV attacks (max 1-2% slippage)
3. **Monitor Gas Prices:** Delay non-urgent transactions during high gas
4. **Use Flashbots:** Prevent front-running on large trades
5. **Check Liquidity:** Ensure sufficient liquidity before trading
6. **Monitor Health Factor:** Keep Aave positions above 1.5 health factor
7. **Set Deadlines:** All transactions should have 5-10 minute deadlines
8. **Approve Token Amounts:** Don't approve unlimited amounts
9. **Use DEX Aggregators:** Get best execution across multiple DEXes
10. **Simulate Transactions:** Use `eth_call` to simulate before sending

## Resources

- **Uniswap V3:** https://docs.uniswap.org/protocol/reference/overview
- **Aave:** https://docs.aave.com/developers/
- **dYdX:** https://docs.dydx.exchange/
- **1inch:** https://docs.1inch.io/
- **Curve:** https://curve.readthedocs.io/
- **Web3.py:** https://web3py.readthedocs.io/
