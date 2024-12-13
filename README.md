# Price Monitor/Alerter
This app looks up the current price for each product in a list, and in case of discount, a notification is sent to interested users via a Telegram bot.

The process runs hourly via Github Actions, and for any price change, a row is added to `./prices.csv` (and commited) for future comparisons.

Visit my [awesome graph page](https://parklez.github.io/price-monitor-alerter/) for the historical data 🤓☝️
![graph-page](docs/page.png)

Here's how Telegram notifications will look like from lockscreen!
![telegram-alert](docs/telegram_alert.jpg)
(more info is shown when opening the message)

### Supported websites:
- www.goimports.com.br
- www.pontofrio.com.br
- www.angeloni.com.br
- www.lg.com

### Setup
This project needs 2 ambient variables in Github Actions's secrets.

- "`PRODUCTS`", which should follow the structure below:
```json
[
  {
    "product_name": "Macbook 14 Pro M3 512GB",
    "url": "https://www.goimports.com.br/Macs/macbook-pro/MacBook-Pro-14-M3-Pro-18GB-512GB-SSD",
    "alerts": { "telegram": ["1234567"] }
  },
  ...
]
```

- "`TELEGRAM_API_TOKEN`" - The Telegram bot token (obtained from @botfather).
