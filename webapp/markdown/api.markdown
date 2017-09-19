# StockStream API

StockStream surfaces data about what stocks have been bought and sold in the Robinhood account as well as who voted for which stock each round. An up-to-date snapshot of the portfolio is available as well. Please see the below documentation for accessing these APIs.


If you have any comments, questions or suggestions about the API or StockStream in general, please join the #development channel in the [StockStream Discord](https://discord.gg/xnrKgEj)

---
## Orders
---
The Orders API surfaces all the orders placed on Robinhood, and their current state. You can use this API to get orders **by date**, **by symbol** or **by id**.

* **date**: To query by date, you must pass the date in the format: *MM-dd-yyyy*. The earliest possible date is **05-30-2017**.
* **symbol**: To query by symbol you must pass the symbol in uppercase.
* **id_list**: To query by id you must pass the list of id's, separated by comma.

---
    http://api.stockstream.live/v1/orders/date/:date
    http://api.stockstream.live/v1/orders/symbol/:symbol
    http://api.stockstream.live/v1/orders?ids=:id_list

    [
       {
          "id":"885e3d109ef091e047313aab39e2d6adfe3f1d83",
          "date":"08/04/2017",
          "symbol":"COST",
          "side":"buy",
          "state":"filled",
          "price":163.98,
          "quantity":1,
          "timestamp":1501867175892,
          "executions":[
             {
                "quantity":"1.00000",
                "timestamp":"2017-08-04T17:12:10.843000Z"
             }
          ]
       },
    ]
---


 * **id**: The ID is represented by a SHA1 hash and has no meaning other than to uniquely identify this order.
 * **date**: The date that this order was place in the format: *MM/dd/yyyy*.
 * **symbol**: The ticker symbol of the stock or ETF that was purchased or sold.
 * **side**: Identifies whether this was a purchase or a sale. Can be either **buy** or **sell**.
 * **state**: The state of the order. Can be **queued**, **unconfirmed**, **confirmed**, **partially_filled**, **filled**, **rejected**, **cancelled**, or **failed**.
 * **price**: The average price of the paid or sale value.
 * **quantity**: The number of shares purchased.
 * **timestamp**: The approximate time stamp that the order was created.
 * **executions (optional)**: Executions may be attached to some orders. These represent executions of the order.
   * **quantity:** The number of shares bought or sold in the execution.
   * **timestamp:** The timestamp of the execution in **UTC**.

---
## Votes
---

The Votes API surfaces the voting choices for each player for each round. This API can be queried **by player** or **by date**.

---
    http://api.stockstream.live/v1/votes/date/:date
    http://api.stockstream.live/v1/votes/player/:player
    http://api.stockstream.live/v1/votes/order/:orderId

 * **date** To query by date, you must pass the date in the format: *MM-dd-yyyy*. For example: *07-25-2017*
 * **player** To query by player you must pass the lowercase username prefixed by **twitch:**. For example: *twitch:stockstream*
 * **orderId** To query by orderId you must pass the id in lowercase. Order ID's can be retrieved from the Order API below.

---
    [
       {
          "username":"twitch:stockstream",
          "date":"08/21/2017",
          "action":"BUY",
          "parameter":"IRDM",
          "timestamp":1503334166257,
          "orderId":"c994127b634a8657d7ebccea8c9c7542413b3da1"
       }
    ]
---

* **username**: The username of the player that voted, prefixed by the platform. Currently only **twitch** is supported.
* **date**: The date that this order was place in the format: *MM/dd/yyyy*. The earliest possible date is **05-30-2017**.
* **action**: The action which the user voted for. Can be either **BUY** or **SELL**.
* **parameter**: The symbol which the user voted to buy or sell.
* **timestamp**: The approximate time stamp that the round of voting ended.
* **orderId (optional)**: If this vote influenced an order, the **id** of the order will be included in the vote structure.

---
# Portfolio
---
You can get the current snapshots by hitting the following endpoint.

    http://api.stockstream.live/v1/portfolio/current

To access historical snapshots, you must first query a date to get a list of the timestamps, then query that timestamp to access the snapshots.

---
    http://api.stockstream.live/v1/portfolio/date/:date
    http://api.stockstream.live/v1/portfolio/date/:date/:timestamp
---

 * **date**: The date the portfolio snapshots were recorded: *MM-dd-yyyy*. The earliest possible date is **06-01-2017**.
 * **timestamp**: The timestamp selected from the list returned by the **date** query. This timestamp represents the approximate GMT time the portfolio snapshot was generated.

Below are some truncated data examples:

---
    [
       "1502456640000",
       "1502492940000"
    ]

    {
       "cashBalance":1510.1799,
       "assets":[
          {
             "symbol":"SINA",
             "shares":1,
             "avgCost":94.5
          },
          {
             "symbol":"WTR",
             "shares":3,
             "avgCost":33.6233
          }
       ]
    }
---


 * **cashBalance**: The amount of spendable cash available.
 * **assets**: The list of assets held in the portfolio:
  * **symbol**: The ticker symbol of the stock held.
  * **shares**: The number of shares held of that stock.
  * **avgCost**: The average cost per share.
