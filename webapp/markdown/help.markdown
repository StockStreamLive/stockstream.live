---
# StockStream Tutorial
---

StockStream is a cooperative multiplayer stock trading game using real money. Below is a tutorial on how to get started playing.

The game is divided into rounds, each lasting between 10 minutes and 60 seconds. At the end of each round the game will count the votes and execute the trade which has the highest votes (or choose randomly in the case of a tie). Each round, one share is bought or sold. During each round, every player is allowed to vote one time, but you can change your vote anytime by voting again.

<br>
<br>

---
# Rounds
---

During each round, players can vote to buy or sell any stock and vote to speed up or slow down the game.

To increase the speed of the game clock by 30 seconds, vote:

> **!faster**

To vote to slow down the game clock by 30 seconds, vote:

> **!slower**

---
# Voting
---

During each round you may vote to buy or sell a stock, and you can change your vote any time you'd like buy simply entering a new vote. You may only sell stocks that are in the [Portfolio](/portfolio).

For example if you want vote to buy a share of Apple, you would type the command:

> **!buy aapl**

Conversely, if you wanted to vote to sell a share of Apple, type the command:

> **!sell aapl**

Once you cast your vote, you should see it show up in the right-hand side of the video.

At any time, you can see the price of a stock and how many shares are in the portfolio by using the **ticker** command. For example, to check Apple, enter the command:

> **!aapl**

***Remember that anyone can vote to sell the stocks you voted for, so choose wisely!***

<br>
<br>

---
# Scoring
---

If you voted for the command that won, then your username will be attached to that order and you'll now have an **open position**. You can see all your open positions on your profile page, which you can find by typing the **!score** command.

When your positions are closed, the game will calculate how much cash was made or lost from your vote. This cash is then added or subtracted from your **wallet balance** (see the next section for how to use your wallet).

<br>
<br>

---
# Wallets
---

Your **#wallet** contains all the cash that you earned from voting for stocks. You can use this cash to manage a private portfolio. Nobody can sell the stocks in your wallet except you, and profits you make trading in your wallet get added to your wallet. Another advantage of your **#wallet** is that orders are executed instantly.

To check your wallet balance, use the **#w** command. To place a trade in your wallet, you must specify the price you are willing to pay. For example if you wanted to buy a share of Apple for $175.35, you would enter the command:

> **\#buy aapl 175.35**

Wallet commands start with the **#** character.

<br>
<br>

---
# Strategy
---

The most important part of the game is deciding what stocks to buy or sell. Fortunately there are many resources available on the Internet to help you find some.


Below are a list of resources to get started playing the game:

* The [StockStream Discord](https://discord.gg/xnrKgEj) channel is a great place for occasional stock discussion and updates on StockStream's new features.

* Investopedia has a great piece on [Short Term Trading](https://goo.gl/H2zEHy).

* Seeking Alpha is also a great resource for stock info. If you're looking for a quick play, check out their [Stock Ideas Section](https://seekingalpha.com/stock-ideas).

* Check out the upcoming [earnings reports](https://www.investopedia.com/terms/e/earningsreport.asp). Earnings reports frequently cause a dramatic shift the price of a stock, so if you're feeling reckless, it's a great place to start.

* Subscribe to the [Cheddar Newsletter](https://cheddar.com/newsletter) for interviews with CEOs and business news.


<br>
<br>


---
# Music and TV
---


StockStream TV is the box in the bottom center of the stream, on StockStream TV you can watch live news, listen to music, and see the latest headlines and tweets of the day. Anyone can change the channel, and anyone can broadcast to the TV.


> **!tv channels** - This command will respond with a list of all the channels that are available.

> **!tv play <channel>** - This command lets you vote to change the channel.

> **!tv add** - Add your twitch channel to the TV. When you're live, your channel will show up in the **!tv channels**.

> **!tv remove** - If you no longer want your twitch channel to be a part of StockStream TV

> **!tv off** - Sick of watching TV? Want to enjoy some peace and quiet? Vote **!tv off** to turn off the **!tv**
