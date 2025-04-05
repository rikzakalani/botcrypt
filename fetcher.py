import aiohttp
import logging

# Daftar API dan fungsi handler-nya
API_SOURCES = [
    "CoinGecko",
    "CoinPaprika",
    "Binance",
    "KuCoin",
    "MEXC",
    "CoinLore",
    "CoinCap"
]

def normalize(symbol, price, p1h, p24h, p7d, p30d, source):
    return {
        "symbol": symbol.upper(),
        "price": float(price),
        "percent_change_1h": float(p1h),
        "percent_change_24h": float(p24h),
        "percent_change_7d": float(p7d),
        "percent_change_30d": float(p30d),
        "sources": [source]
    }

async def fetch_all_data():
    coins = []

    async with aiohttp.ClientSession() as session:
        for source in API_SOURCES:
            try:
                logging.info(f"Fetching data from {source}")
                if source == "CoinGecko":
                    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
                    async with session.get(url) as res:
                        data = await res.json()
                        for c in data:
                            coins.append(normalize(
                                c["symbol"],
                                c["current_price"],
                                c.get("price_change_percentage_1h_in_currency", 0),
                                c.get("price_change_percentage_24h_in_currency", 0),
                                c.get("price_change_percentage_7d_in_currency", 0),
                                c.get("price_change_percentage_30d_in_currency", 0),
                                source
                            ))

                elif source == "CoinPaprika":
                    url = "https://api.coinpaprika.com/v1/tickers"
                    async with session.get(url) as res:
                        data = await res.json()
                        for c in data:
                            usd = c.get("quotes", {}).get("USD", {})
                            coins.append(normalize(
                                c["symbol"],
                                usd.get("price", 0),
                                usd.get("percent_change_1h", 0),
                                usd.get("percent_change_24h", 0),
                                usd.get("percent_change_7d", 0),
                                usd.get("percent_change_30d", 0),
                                source
                            ))

                elif source == "Binance":
                    url = "https://api.binance.com/api/v3/ticker/24hr"
                    async with session.get(url) as res:
                        data = await res.json()
                        for c in data:
                            symbol = c["symbol"].upper().replace("USDT", "")
                            coins.append(normalize(
                                symbol,
                                c.get("lastPrice", 0),
                                0,
                                c.get("priceChangePercent", 0),
                                0,
                                0,
                                source
                            ))

                elif source == "KuCoin":
                    url = "https://api.kucoin.com/api/v1/market/allTickers"
                    async with session.get(url) as res:
                        data = await res.json()
                        for c in data["data"]["ticker"]:
                            symbol = c["symbolName"].replace("-USDT", "")
                            coins.append(normalize(
                                symbol,
                                c.get("last", 0),
                                0, c.get("changeRate", 0), 0, 0,
                                source
                            ))

                elif source == "MEXC":
                    url = "https://api.mexc.com/api/v3/ticker/24hr"
                    async with session.get(url) as res:
                        data = await res.json()
                        for c in data:
                            symbol = c["symbol"].replace("USDT", "")
                            coins.append(normalize(
                                symbol,
                                c["lastPrice"],
                                0, c["priceChangePercent"], 0, 0,
                                source
                            ))

                elif source == "CoinLore":
                    url = "https://api.coinlore.net/api/tickers/"
                    async with session.get(url) as res:
                        data = await res.json()
                        for c in data["data"]:
                            coins.append(normalize(
                                c["symbol"],
                                c["price_usd"],
                                c.get("percent_change_1h", 0),
                                c.get("percent_change_24h", 0),
                                c.get("percent_change_7d", 0),
                                0,
                                source
                            ))

                elif source == "CoinCap":
                    url = "https://api.coincap.io/v2/assets"
                    async with session.get(url) as res:
                        data = await res.json()
                        for c in data["data"]:
                            coins.append(normalize(
                                c["symbol"],
                                c["priceUsd"],
                                0,
                                c.get("changePercent24Hr", 0),
                                0, 0,
                                source
                            ))

                logging.info(f"✅ {source} OK - total coin ditambahkan: {len(coins)}")

            except Exception as e:
                logging.error(f"❌ Gagal fetch dari {source}: {e}")

    return merge_duplicates(coins)

def merge_duplicates(coins):
    merged = {}
    for coin in coins:
        symbol = coin["symbol"]
        if symbol not in merged:
            merged[symbol] = coin
        else:
            merged[symbol]["sources"].extend(coin["sources"])
    return list(merged.values())

def filter_and_sort(coins):
    filtered = [
        c for c in coins if c["price"] > 0 and
        c["percent_change_1h"] > 0 and
        c["percent_change_24h"] > 0 and
        c["percent_change_7d"] > 0 and
        c["percent_change_30d"] > 0
    ]
    return sorted(filtered, key=lambda x: x["price"])

def format_coin_data(coins):
    output = []
    for c in coins:
        output.append(
            f"<b>{c['symbol']}</b> – ${c['price']:.10f}\n"
            f"↳ +{c['percent_change_1h']:.2f}% 1h, "
            f"+{c['percent_change_24h']:.2f}% 24h, "
            f"+{c['percent_change_7d']:.2f}% 7d, "
            f"+{c['percent_change_30d']:.2f}% 30d\n"
            f"↳ <i>Sumber: {', '.join(set(c['sources']))}</i>"
        )
    return "\n\n".join(output)
