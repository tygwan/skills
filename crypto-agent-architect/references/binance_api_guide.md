# Binance API Integration Guide

Comprehensive guide for integrating Binance API into crypto trading agents.

## API Endpoints

### Base URLs

```python
PRODUCTION = "https://api.binance.com"
TESTNET = "https://testnet.binance.vision"
```

Always use **Testnet** for development and testing.

### REST API

**Market Data:**
- `GET /api/v3/ticker/24hr` - 24hr ticker price change
- `GET /api/v3/ticker/price` - Current price
- `GET /api/v3/depth` - Order book depth
- `GET /api/v3/klines` - Candlestick data

**Account:**
- `GET /api/v3/account` - Account information
- `GET /api/v3/myTrades` - Trade history

**Trading:**
- `POST /api/v3/order` - Place order
- `DELETE /api/v3/order` - Cancel order
- `GET /api/v3/order` - Query order

### WebSocket Streams

**Real-time Data:**
- `wss://stream.binance.com:9443/ws/<symbol>@ticker` - Ticker updates
- `wss://stream.binance.com:9443/ws/<symbol>@depth` - Order book updates
- `wss://stream.binance.com:9443/ws/<symbol>@trade` - Trade updates
- `wss://stream.binance.com:9443/ws/<symbol>@kline_<interval>` - Candlestick updates

**Example:**
```python
import websockets
import json

async def subscribe_ticker(symbol: str):
    uri = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@ticker"

    async with websockets.connect(uri) as ws:
        async for message in ws:
            data = json.loads(message)
            print(f"Price: {data['c']}")  # Current close price
```

## Rate Limits

### Request Weight System

Binance uses a **request weight** system where each endpoint has a weight:

- **Order book:** Weight 1-50 (depends on limit)
- **Place order:** Weight 1
- **Account info:** Weight 10
- **Trade history:** Weight 10

**Limits:**
- **1200 weight per minute** per IP
- **10 orders per second** per account
- **100,000 orders per day** per account

### Rate Limit Headers

```python
X-MBX-USED-WEIGHT-1M: 50  # Weight used in last minute
X-MBX-ORDER-COUNT-10S: 5  # Orders in last 10 seconds
```

**Implementation:**

```python
class RateLimiter:
    def __init__(self):
        self.weight_per_minute = 1200
        self.current_weight = 0
        self.last_reset = time.time()

    def check_and_update(self, weight: int):
        """Check if request would exceed limit."""

        # Reset counter every minute
        if time.time() - self.last_reset > 60:
            self.current_weight = 0
            self.last_reset = time.time()

        if self.current_weight + weight > self.weight_per_minute:
            raise RateLimitExceeded("Rate limit would be exceeded")

        self.current_weight += weight
```

## Authentication

### API Keys

1. Create API key in Binance account settings
2. **Enable IP whitelist** for production
3. Set appropriate permissions (read, trade, withdraw)

### HMAC SHA256 Signature

All **signed** endpoints require signature:

```python
import hmac
import hashlib
import time

def sign_request(params: dict, api_secret: str) -> str:
    """Generate HMAC SHA256 signature."""

    # Add timestamp
    params['timestamp'] = int(time.time() * 1000)

    # Create query string
    query_string = '&'.join(f"{k}={v}" for k, v in params.items())

    # Generate signature
    signature = hmac.new(
        api_secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return signature
```

**Example Request:**

```python
import requests

def get_account_info(api_key: str, api_secret: str):
    """Get account information."""

    url = "https://api.binance.com/api/v3/account"

    params = {
        'timestamp': int(time.time() * 1000)
    }

    signature = sign_request(params, api_secret)
    params['signature'] = signature

    headers = {
        'X-MBX-APIKEY': api_key
    }

    response = requests.get(url, params=params, headers=headers)
    return response.json()
```

## Order Types

### Market Order

Execute immediately at current market price:

```python
{
    "symbol": "BTCUSDT",
    "side": "BUY",  # or "SELL"
    "type": "MARKET",
    "quantity": 0.001
}
```

### Limit Order

Execute at specified price or better:

```python
{
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "LIMIT",
    "timeInForce": "GTC",  # Good Till Cancel
    "quantity": 0.001,
    "price": 45000
}
```

### Stop-Loss Order

Trigger market order when price reaches stop price:

```python
{
    "symbol": "BTCUSDT",
    "side": "SELL",
    "type": "STOP_LOSS",
    "quantity": 0.001,
    "stopPrice": 44000
}
```

### Stop-Loss Limit Order

Trigger limit order when price reaches stop price:

```python
{
    "symbol": "BTCUSDT",
    "side": "SELL",
    "type": "STOP_LOSS_LIMIT",
    "timeInForce": "GTC",
    "quantity": 0.001,
    "price": 43900,
    "stopPrice": 44000
}
```

## Order Filters

Binance enforces filters on all orders. Get filters via `/api/v3/exchangeInfo`.

### LOT_SIZE

Controls quantity precision:

```json
{
    "filterType": "LOT_SIZE",
    "minQty": "0.00100000",
    "maxQty": "100000.00000000",
    "stepSize": "0.00100000"
}
```

**Validation:**
```python
def validate_quantity(quantity: float, min_qty: float, max_qty: float, step_size: float):
    """Validate quantity against LOT_SIZE filter."""

    if quantity < min_qty:
        raise ValueError(f"Quantity {quantity} below minimum {min_qty}")

    if quantity > max_qty:
        raise ValueError(f"Quantity {quantity} above maximum {max_qty}")

    # Check step size
    if (quantity - min_qty) % step_size != 0:
        raise ValueError(f"Quantity {quantity} not a multiple of step size {step_size}")
```

### PRICE_FILTER

Controls price precision:

```json
{
    "filterType": "PRICE_FILTER",
    "minPrice": "0.01000000",
    "maxPrice": "1000000.00000000",
    "tickSize": "0.01000000"
}
```

### MIN_NOTIONAL

Minimum order value (price × quantity):

```json
{
    "filterType": "MIN_NOTIONAL",
    "minNotional": "10.00000000"
}
```

**Validation:**
```python
def validate_notional(price: float, quantity: float, min_notional: float):
    """Validate order meets minimum notional."""

    notional = price * quantity

    if notional < min_notional:
        raise ValueError(
            f"Order notional {notional} below minimum {min_notional}"
        )
```

## Error Codes

### Common Errors

| Code | Message | Solution |
|------|---------|----------|
| -1000 | UNKNOWN | Check request format |
| -1001 | DISCONNECTED | Reconnect |
| -1002 | UNAUTHORIZED | Check API key |
| -1003 | TOO_MANY_REQUESTS | Rate limit exceeded, back off |
| -1021 | TIMESTAMP_OUT_OF_SYNC | Sync system time (NTP) |
| -2010 | INSUFFICIENT_BALANCE | Insufficient funds |
| -2011 | UNKNOWN_ORDER | Order not found |
| -1013 | INVALID_QUANTITY | Check LOT_SIZE filter |
| -1111 | PRECISION_OVER_MAX | Round to correct precision |

### Error Handling

```python
class BinanceAPIException(Exception):
    """Binance API error."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance error {code}: {message}")

def handle_binance_error(response):
    """Handle Binance API errors."""

    if response.status_code == 200:
        return response.json()

    error = response.json()
    code = error.get('code', -1000)
    msg = error.get('msg', 'Unknown error')

    if code == -1003:  # Rate limit
        raise RateLimitExceeded(msg)
    elif code == -2010:  # Insufficient balance
        raise InsufficientBalance(msg)
    elif code == -1021:  # Timestamp sync
        raise TimestampOutOfSync(msg)
    else:
        raise BinanceAPIException(code, msg)
```

## Time Synchronization

Binance requires timestamp within **5000ms** of server time.

### NTP Sync

```python
import ntplib
from time import ctime

def sync_time():
    """Sync time with NTP server."""

    client = ntplib.NTPClient()
    response = client.request('pool.ntp.org')

    offset_ms = response.offset * 1000

    print(f"Time offset: {offset_ms:.0f}ms")

    if abs(offset_ms) > 5000:
        raise Exception("System time out of sync by >5s")

    return offset_ms

# Get server time
def get_server_time():
    """Get Binance server time."""

    response = requests.get("https://api.binance.com/api/v3/time")
    return response.json()['serverTime']
```

## Best Practices

### 1. Use Testnet First

Always test on Testnet before going live:

```python
class BinanceClient:
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = (
            "https://testnet.binance.vision" if testnet
            else "https://api.binance.com"
        )
```

### 2. Implement Rate Limiting

Prevent hitting rate limits:

```python
from functools import wraps
from time import sleep

def rate_limit(max_calls: int, period: int):
    """Rate limiting decorator."""

    def decorator(func):
        calls = []

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()

            # Remove old calls
            calls[:] = [c for c in calls if now - c < period]

            if len(calls) >= max_calls:
                sleep_time = period - (now - calls[0])
                sleep(sleep_time)

            calls.append(time.time())
            return func(*args, **kwargs)

        return wrapper
    return decorator

@rate_limit(max_calls=1200, period=60)
def api_call():
    pass
```

### 3. Use Circuit Breaker

Prevent cascading failures:

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.state = "closed"  # closed, open, half_open
        self.last_failure_time = None

    def call(self, func):
        if self.state == "open":
            if time.time() - self.last_failure_time > 60:
                self.state = "half_open"
            else:
                raise Exception("Circuit breaker open")

        try:
            result = func()
            self.failure_count = 0
            self.state = "closed"
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "open"

            raise
```

### 4. Cache Static Data

Cache exchange info, symbol filters:

```python
import redis

class BinanceCache:
    def __init__(self, redis_client):
        self.redis = redis_client

    def get_exchange_info(self, symbol: str):
        """Get cached exchange info."""

        key = f"exchange_info:{symbol}"
        cached = self.redis.get(key)

        if cached:
            return json.loads(cached)

        # Fetch from API
        info = fetch_exchange_info(symbol)

        # Cache for 1 hour
        self.redis.set(key, json.dumps(info), ex=3600)

        return info
```

### 5. Use WebSockets for Real-Time Data

REST API has delays, use WebSockets for real-time:

```python
async def subscribe_orderbook(symbol: str, callback):
    """Subscribe to order book updates."""

    uri = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@depth"

    while True:
        try:
            async with websockets.connect(uri) as ws:
                async for message in ws:
                    data = json.loads(message)
                    await callback(data)
        except websockets.ConnectionClosed:
            print("WebSocket closed, reconnecting...")
            await asyncio.sleep(5)
```

## Security

### API Key Permissions

Set minimum required permissions:

- **Read Only:** For monitoring/analysis
- **Spot Trading:** For trading (no withdrawals)
- **Withdrawals:** Never enable for trading bots

### IP Whitelisting

Always use IP whitelisting in production:

```python
# In Binance account settings:
# API Management > Edit API > IP Access Restrictions
# Add server IPs only
```

### Secure Storage

Never hardcode API keys:

```python
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
```

## Testing

### Testnet Setup

1. Visit https://testnet.binance.vision/
2. Register test account
3. Generate API keys
4. Fund account with test USDT

### Example Test

```python
import pytest

@pytest.mark.integration
async def test_place_order_testnet():
    """Test order placement on Testnet."""

    client = BinanceAdapter(
        api_key=TESTNET_KEY,
        api_secret=TESTNET_SECRET,
        testnet=True
    )

    order = await client.place_order(
        symbol="BTCUSDT",
        side="BUY",
        order_type="LIMIT",
        quantity=0.001,
        price=40000
    )

    assert order.status in ["NEW", "FILLED"]
```

## Resources

- **Official Docs:** https://binance-docs.github.io/apidocs/spot/en/
- **Testnet:** https://testnet.binance.vision/
- **Python SDK:** https://github.com/binance/binance-connector-python
- **Rate Limits:** https://binance-docs.github.io/apidocs/spot/en/#limits
- **Error Codes:** https://binance-docs.github.io/apidocs/spot/en/#error-codes
