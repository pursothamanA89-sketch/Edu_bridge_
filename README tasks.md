# Trading Data Cleaning Test (Synthetic Data)

**Files**
- `trades_orderbook_STUDENT_dirty.csv` - give this to students (2,035 rows, deliberately messy)
- `trades_orderbook_clean_ANSWER_KEY.csv` - keep this for yourself (2,000 clean rows)

All data is synthetic (simulated BTCUSDT), not real market data.

**Columns:** each row is one trade plus the order book snapshot at that moment (top 3 bid and ask levels: price and quantity).

**Hidden problems students should find**
1. Duplicate rows (35)
2. Missing values in price, quantity, side, bid_qty_1, ask_price_1
3. Mixed timestamp formats (standard, DD/MM/YYYY, and Unix milliseconds)
4. Inconsistent `side` labels (buy, BUY, Sell)
5. Inconsistent `symbol` names (BTCUSDT, btcusdt, BTC/USDT, BTC-USDT)
6. Prices stored as text with $ and commas
7. Outlier prices (x100) and negative prices
8. Zero quantities
9. Crossed order book (best bid higher than best ask)
10. Rows in random order

**Student tasks**
1. Load the file and report all data quality issues found.
2. Clean it (Python/pandas or Excel) and explain every decision, such as drop vs fill.
3. Sort by time and remove duplicates by `trade_id`.
4. Add columns: `spread` (ask_1 - bid_1), `mid_price`, and `order_imbalance` = (bid_qty_1 - ask_qty_1) / (bid_qty_1 + ask_qty_1).
5. Resample to 1-minute OHLCV candles.

**Scoring idea:** compare the student's cleaned file to the answer key (row count, missing values, and matching prices).
