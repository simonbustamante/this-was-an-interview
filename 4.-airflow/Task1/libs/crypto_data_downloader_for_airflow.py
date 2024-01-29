import argparse
import requests
import json
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Float, Date, select, func, JSON
from sqlalchemy.dialects.postgresql import insert

# Setting logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CryptoDataDownloader:
    def __init__(self, coin_id, date):
        self.coin_id = coin_id
        self.date = date
        self.formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")
        self.url = f"https://api.coingecko.com/api/v3/coins/{self.coin_id}/history?date={self.formatted_date}"

    def download_data(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            logging.info("Data downloaded successfully")
            return response.json()
        else:
            logging.error(f"Failed to retrieve data: {response.status_code}")
            raise Exception(f"Failed to retrieve data: {response.status_code}")

    def save_data_to_file(self, data):
        filename = f"{self.coin_id}_{self.date}.json"
        with open(filename, 'w') as file:
            json.dump(data, file)
        logging.info(f"Data saved to {filename}")

class MainApplicationForAirFlow:
    def __init__(self, coin_id, date=None, start_date=None, end_date=None, workers=3, db=False):
        #command line arguments
        self.coin_id = coin_id
        self.date = date
        self.start_date = start_date
        self.end_date = end_date
        self.workers = workers
        self.db = db
        self.engine = create_engine('postgresql://airflow:airflow@postgres:5432/airflow')
        self.metadata = MetaData()
        self.coin_data_table = Table('coin_data', self.metadata,
                                Column('coin', String, primary_key=True),
                                Column('date', Date, primary_key=True),
                                Column('price', Float),
                                Column('json', JSON),
                           )
        self.coin_month_data_table = Table('coin_month_data', self.metadata,
                                Column('coin', String, primary_key=True),
                                Column('year', Integer, primary_key=True),
                                Column('month', Integer, primary_key=True),
                                Column('min_price', Float),
                                Column('max_price', Float),
                           )
        self.metadata.create_all(self.engine)

    def insert_or_update_coin_data(self, conn, coin_id, date, price, data):
        stmt = insert(self.coin_data_table).values(
            coin=coin_id, date=date, price=price, json=data
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=['coin', 'date'],
            set_=dict(price=price, json=data)
        )
        logging.info("Inserting or updating data for %s on %s: Price - %s", coin_id, date, price)
        conn.execute(stmt)
        conn.commit()

    def insert_or_update_month_data(self, conn, coin_id, date):
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d")
        min_max_price = self.getMaxAndMin(conn, coin_id, date)
        logging.info("Calculating max and min %s for Coin Id %s on date %s", min_max_price,coin_id, date)
        if min_max_price:
            month_stmt = insert(self.coin_month_data_table).values(
                coin=coin_id, year=date.year, month=date.month,
                min_price=min_max_price.min_price, max_price=min_max_price.max_price
            )
            month_stmt = month_stmt.on_conflict_do_update(
                index_elements=['coin', 'year', 'month'],
                set_=dict(min_price=min_max_price.min_price, max_price=min_max_price.max_price)
            )
            conn.execute(month_stmt)
            conn.commit()

    def getMaxAndMin(self,conn, coin_id, date):
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d")
        logging.info(f"Calculating Max and Min for {coin_id} in {date}")

        query = select(
            func.min(self.coin_data_table.c.price).label("min_price"),
            func.max(self.coin_data_table.c.price).label("max_price")
        ).where(
            (self.coin_data_table.c.coin == coin_id) &
            (func.extract('month', self.coin_data_table.c.date) == date.month) &
            (func.extract('year', self.coin_data_table.c.date) == date.year)
        )

        result = conn.execute(query)
        result = result.fetchone()
        logging.info(f"Result: {result}")
        return result
    
    def save_data_to_db(self, coin_id, date, data):
        price = data.get('market_data', {}).get('current_price', {}).get('usd')
        if price is None:
            return
        logging.info(f"Saving on postgresql")
        with self.engine.connect() as conn:
            self.insert_or_update_coin_data(conn, coin_id, date, price, data)
            self.insert_or_update_month_data(conn, coin_id, date)
    

    def process_single_day(self, date=None):
        if date is None:
            date = self.date
        #date = datetime.strptime(date, "%Y-%m-%d")
        downloader = CryptoDataDownloader(self.coin_id, date)
        try:
            data = downloader.download_data()
            logging.info(f"Saving data for {date}")
            downloader.save_data_to_file(data)
            if self.db:
                logging.info(f"Saving data for {date} on db")
                self.save_data_to_db(self.coin_id, date, data)
        except Exception as e:
            logging.error(f"Error processing {date}: {e}")

    def process_bulk_days(self):
        start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
        dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = [executor.submit(self.process_single_day, date.strftime("%Y-%m-%d")) for date in dates]
            for future in futures:
                future.result()


    def run(self):
        if self.date:
            self.process_single_day()
        elif self.start_date and self.end_date:
            self.process_bulk_days()
        else:
            logging.error("Invalid arguments: Please provide either a single date or a start and end date.")       

# if __name__ == "__main__":
#     app = MainApplicationForAirFlow(coin_id="bitcoin", date="2024-10-10")
#     app.run()
