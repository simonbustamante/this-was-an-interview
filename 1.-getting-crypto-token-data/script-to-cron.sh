#!/bin/bash

# get current date YYYY-MM-DD
current_date=$(date +%Y-%m-%d)

/usr/bin/python3.11 crypto_data_downloader.py --date $current_date --coin-id bitcoin
/usr/bin/python3.11 crypto_data_downloader.py --date $current_date --coin-id ethereum
/usr/bin/python3.11 crypto_data_downloader.py --date $current_date --coin-id cardano