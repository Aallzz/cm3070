# Market Data Fetching


### Before start

I want to try using rabbit message queue, so that when processes are restarted we have all needed messages. There is still some work to do to finish this. The point is you need to run the following 

```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install -y erlang
<!-- echo "deb https://dl.bintray.com/rabbitmq-erlang/debian buster erlang" | sudo tee /etc/apt/sources.list.d/bintray.rabbitmq.list
curl -s https://dl.bintray.com/rabbitmq-erlang/debian/rabbitmq-release-signing-key.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get install -y rabbitmq-server -->
<!-- From https://www.rabbitmq.com/docs/install-debian -->
sudo apt-get install curl gnupg apt-transport-https -y

## Team RabbitMQ's main signing key
curl -1sLf "https://keys.openpgp.org/vks/v1/by-fingerprint/0A9AF2115F4687BD29803A206B73A36E6026DFCA" | sudo gpg --dearmor | sudo tee /usr/share/keyrings/com.rabbitmq.team.gpg > /dev/null
## Community mirror of Cloudsmith: modern Erlang repository
curl -1sLf https://github.com/rabbitmq/signing-keys/releases/download/3.0/cloudsmith.rabbitmq-erlang.E495BB49CC4BBE5B.key | sudo gpg --dearmor | sudo tee /usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg > /dev/null
## Community mirror of Cloudsmith: RabbitMQ repository
curl -1sLf https://github.com/rabbitmq/signing-keys/releases/download/3.0/cloudsmith.rabbitmq-server.9F4587F226208342.key | sudo gpg --dearmor | sudo tee /usr/share/keyrings/rabbitmq.9F4587F226208342.gpg > /dev/null

## Add apt repositories maintained by Team RabbitMQ
sudo tee /etc/apt/sources.list.d/rabbitmq.list <<EOF
## Provides modern Erlang/OTP releases
##
deb [arch=amd64 signed-by=/usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg] https://ppa1.rabbitmq.com/rabbitmq/rabbitmq-erlang/deb/ubuntu noble main
deb-src [signed-by=/usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg] https://ppa1.rabbitmq.com/rabbitmq/rabbitmq-erlang/deb/ubuntu noble main

# another mirror for redundancy
deb [arch=amd64 signed-by=/usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg] https://ppa2.rabbitmq.com/rabbitmq/rabbitmq-erlang/deb/ubuntu noble main
deb-src [signed-by=/usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg] https://ppa2.rabbitmq.com/rabbitmq/rabbitmq-erlang/deb/ubuntu noble main

## Provides RabbitMQ
##
deb [arch=amd64 signed-by=/usr/share/keyrings/rabbitmq.9F4587F226208342.gpg] https://ppa1.rabbitmq.com/rabbitmq/rabbitmq-server/deb/ubuntu noble main
deb-src [signed-by=/usr/share/keyrings/rabbitmq.9F4587F226208342.gpg] https://ppa1.rabbitmq.com/rabbitmq/rabbitmq-server/deb/ubuntu noble main

# another mirror for redundancy
deb [arch=amd64 signed-by=/usr/share/keyrings/rabbitmq.9F4587F226208342.gpg] https://ppa2.rabbitmq.com/rabbitmq/rabbitmq-server/deb/ubuntu noble main
deb-src [signed-by=/usr/share/keyrings/rabbitmq.9F4587F226208342.gpg] https://ppa2.rabbitmq.com/rabbitmq/rabbitmq-server/deb/ubuntu noble main
EOF

## Update package indices
sudo apt-get update -y

## Install Erlang packages
sudo apt-get install -y erlang-base \
                        erlang-asn1 erlang-crypto erlang-eldap erlang-ftp erlang-inets \
                        erlang-mnesia erlang-os-mon erlang-parsetools erlang-public-key \
                        erlang-runtime-tools erlang-snmp erlang-ssl \
                        erlang-syntax-tools erlang-tftp erlang-tools erlang-xmerl

## Install rabbitmq-server and its dependencies
sudo apt-get install rabbitmq-server -y --fix-missing



sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server
sudo rabbitmq-plugins enable rabbitmq_management

## Aws cli 

# Chnage directory to tmp, for removal of installation files.
cd /tmp

# Install AWS CLI.
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install



## Deletion scheduling depenancies 

sudo apt-get install at
sudo systemctl start atd
sudo systemctl enable atd

```

### Start

To start writing market data to the local computer from supported exchanges in the format described in "format" section  run the following command in your script 
```
python python/market_data/data_recorder.py 
```

The script will create a folder data where it will put all results for the fetchers. Be carefull running it from your laptop, because if you don't stop the recorder processes you will end up with a ton of data.

Also it will create a file called process_registry.txt, where it will put what files are currently being processed. This file is used to prevent many processes run at the same time.

> Note: If you have to interrupt the process of fetching the data, please do so using the following instrutions
```
pkill -f python/market_data/data_recorder.py
rm -rf process_registry.txt 
```

### Tips 

> Note: To verify that processes stopped successfully run 
```
pgrep -f "python python/market_data/data_recorder.py"
``` 

> Note: You can check recorder logs by
```
tail -f logs.txt
``` 

> Note: To check that files in data grow in side 
```
tree data/ --du 
``` 

> Note: To check the message queues
```
rabbitmqadmin list queues
``` 


> Note: if it's not working make sure that PYTHONPATH set up correctly
```
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

> Note: make sure you set up the environement for python and install all libraries from requirements.txt at the root of the file 
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> Note: to upload files to AWS S4
```
find data -type f -path '*/2024-May/*' -regex '.*/\([0-9]\|1[0-9]\|2[0-4]\)\.csv$' | while read file; do
    aws s3 cp "$file" "s3://marketdata/${file#data/}"
done

find data -type f -path '*/2024-May/*' -regex '.*/\([0-9]\|1[0-9]\|2[0-4]\)\.csv$' -exec rm {} +
```

## AWS sync

```
sudo -E ./python/market_data/aws_data_sync_script.sh
```


## Market Data Fetchers 

A fetcher is a class responsible for collecting data from one exchange of one specified asset type for one or more instruments through websocket API.

The list of supported fetchers can be found in ***python/market_data/fetchers/__init__.py***. Every market data fetcher must be a child of MarketDataFetcher, that will require fetcher to specify the method of fetching and data needed for the recording to the files. 

### Format

- Server Timestamp — long int, unix timestamp since epoch UTC.
- Exchange timestamp(Optional) - long in, unix timestamp since epoch UTC.
- Tick Type(EntryType in code) — (0 — Bid, 1 — Ask, 2 — Trade) type of the tick
- Update Type — (0 — New, 1 — Update, 2 — Delete, 3 - Sell, 4 - Buy) what to do with the update (update existing level, delete level or that’s snapshot) NEW ⇒ means that’s snapshot. Update/Delete ⇒ means incremental order book update
    - If current row = 0 (i.e. NEW), then clear current status of order book and read rows with update type = NEW until update type ≠ NEW
    - if current row = 1/2 (UPDATE / DELETE) then either do orderbook[price][tick type] = size or del orderbook[price][tick type] (unless obv. tick type = trade, as it’s only for bid and ask)
- Price — float, level
- Size — float, size on that level

### Onboarding a new fetcher

To onboard a new fetcher you need to 

1) Create a ***fetcher.py*** in **python/market_data/fetchers/<exchange_name>/<asset_type/fetcher.py***. In the file there must be a class that extends **MarketDataFetcher**, this is an abstract class that will require you to provide information: 
  
    1. Exchange name, asset type - those will be used to create a path for csv file 
    2. Supported instruments and supported instruments for test - instuments that will be recorded to separate CSV files as described in "Format" section
    3. Websocket endpoint, subscription arguments - parameters that will be used to create a connection to the exchange
    4. Response transform function - a function that will transform JSON to TickRecord, that defines how the data will be writted in csv files

2. [OPTIONAL] For response transform function use your best judjements where to put it, usually it's shared between asset types, so I\'ve put it in **python/market_data/fetchers/<exchange_name>/data_transformer.py**. 

3. Add the new fetcher to ***python/market_data/fetchers/__init__.py*** 

### Hyperliquid (only Perp)

***HyperliquidMarketDataFetcher*** - market data fetcher for [hyperliquid](https://hyperliquid.xyz/) exchange perp futures. Some qualities of this data
* Exchange trades only perpetual futures 
* Instument name is \<SYMBOL> with assumption that it is always against USDC
* API provides only order book snapshots, no orders 
* API has a limited number of order book levels - 10
* API can provide trades


### OKX (Spot and Perp)

***OKXSpotMarketDataFetcher*** - market data fetcher for [okx](https://www.okx.com/) exchange spot - [doc](https://www.okx.com/docs-v5/en/#order-book-trading-market-data-ws-all-trades-channel)
***OKXPerpMarketDataFetcher*** - market data fetcher for [okx](https://www.okx.com/) exchange perp - [doc](https://www.okx.com/docs-v5/en/#order-book-trading-market-data-ws-all-trades-channel) 

* Both spot and perp use the same wb endpoint.
* Instument name for spot is \<SYMBOL>-\<SYMBOL>
* Instrument name for perp is \<SYMBOL>-\<SYMBOL>-SWAP 
* Currently it's using books channel, because for better options (except books5) we need to be VIP users. From the documentation it's characterised as ```400 depth levels will be pushed in the initial full snapshot. Incremental data will be pushed every 100 ms for the changes in the order book during that period of time.``` 



### Bybit (Spot and Perp)

***BybitSpotMarketDataFetcher*** - market data fetcher for [bybit](https://www.bybit.com/) exchange spot - [doc](https://bybit-exchange.github.io/docs/v5/websocket/public/orderbook)
***BybitPerpMarketDataFetcher*** - market data fetcher for [bybit](https://www.bybit.com/) exchange perp - [doc](https://bybit-exchange.github.io/docs/v5/websocket/public/orderbook)

* Currently it's using [order books api](https://bybit-exchange.github.io/docs/spot/ws-public/orderbook), but spot and prep differ in endpoints. 

* Depth: 40 each for asks and bids.
* Events trigger order book version change:
  * order enters order book
  * order leaves order book
  * order quantity changes
  * order filled
* Pushes snapshot data only
* Push frequency: 100ms
