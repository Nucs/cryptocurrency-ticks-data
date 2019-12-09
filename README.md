# cryptocurrency-ticks-data
---

550 days of trade ticks on BTC, ETH, LTC, BNB, NEO, QTUM to USTD or BTC
![alt text](https://i.imgur.com/wRK5UBW.png)
<br><br>

The data is stored inside a regular zip file. inside every zip there is a .csv file in plain text.<br>
The data consists of the following columns:
1. Id - id provided by the exchange
2. time - epoch time, UTC. There might be a 1-3h (consistent) offset accidentally added by C# automatic localization of DateTime. I have no way to verify if this is true.
3. Price - The price in the rhs symbol (e.g. BTCUSDT means price is in USDT)
4. Quantity - Quantity of the lhs symbol (e.g. BTCUSDT means quantity in BTC)
5. IsBuyerMaker - was the trade completed by the buyer (true) or by the seller (false). 
    when it is true, it means that the seller has placed a ask for his holdings and a buyer came along later on and completed the trade.
    when it is false, it means that the buyer has placed a bid for his curreny and a seller came along later on and completed the trade.
6. BuyerOrderId - Order id of the buyer
7. SellerOrderId - Order id of the seller
8. IsBestPriceMatch - Has the Maker (buyermaker or sellermaker) accomplished the trade by a market order as opposed to a trade accomplished by a limit order which waits for an opposite trade pair (I might be wrong tho, this need verification).
