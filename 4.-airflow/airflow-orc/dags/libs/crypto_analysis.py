import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CryptoAnalysis:

    def __init__(self, coin_id, db_connection_string='postgresql://airflow:airflow@postgres:5432/airflow'):
        self.coin_id = coin_id
        self.engine = create_engine(db_connection_string)
    
    def plot_prices(self, days=30):
        query = f"""
        SELECT date, price
        FROM coin_data
        WHERE coin = '{self.coin_id}'
        ORDER BY date DESC
        LIMIT {days}
        """
        df = pd.read_sql(query, self.engine)
        df.set_index('date', inplace=True)
        plt.figure(figsize=(10, 5))
        plt.plot(df['price'], label='Price')
        plt.title(f'{self.coin_id.capitalize()} Price Last {days} Days')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        logging.info(f'It has been generated the image {self.coin_id}_prices_during_30days.png')
        plt.savefig(f'{self.coin_id}_prices_during_30_days_'+ datetime.now().strftime("%Y-%m-%d_%H:%M:%S") +'.png')
        plt.close()
        print(f"Saved plot for {self.coin_id}.")

    def calculate_average_difference(self, days=30):
        query = f"""
        SELECT date, price
        FROM coin_data
        WHERE coin = '{self.coin_id}'
        ORDER BY date DESC
        LIMIT {days}
        """
        df = pd.read_sql(query, self.engine)
        df['difference'] = df['price'].diff() 
        df.dropna(inplace=True) 
        average_difference = df['difference'].mean()
        logging.info(f"The average difference in price for the last {days} days is: {average_difference}")
        


if __name__ == "__main__":
    coin_id = "bitcoin"  
    analysis = CryptoAnalysis(coin_id)
    analysis.plot_prices(days=30)
    analysis.calculate_average_difference(days=30)
    