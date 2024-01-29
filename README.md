# Usage Guide - Simon Bustamante's Exam

## Table of Contents

- [0. Code Cloning](#0-code-cloning)
- [0.1. Pre-requisites](#01-pre-requisites)
- [1. Getting Crypto Token Data](#1-getting-crypto-token-data)
  - [1.1. Task 1 - Crypto Data Downloader](#11-task-1---crypto-data-downloader)
  - [1.2. Task 2 - Automation with CRON](#12-task-2---automation-with-cron)
  - [1.3. Task 3 - Adding Bulk Processing Support](#13-task-3---adding-bulk-processing-support)
- [2. Loading Data into the Database](#2-loading-data-into-the-database)
  - [2.1. Task 1 - Installing PostgreSQL with Two Tables](#21-task-1---installing-postgresql-with-two-tables)
  - [2.2. Task 2 - Enabling Data Storage on PostgreSQL](#22-task-2---enabling-data-storage-on-postgresql)
- [3. Analysing Coin Data with SQL](#3-analysing-coin-data-with-sql)
  - [3.1. Task 1 - Get the Average Price for Each Coin by Month](#31-task-1---get-the-average-price-for-each-coin-by-month)
  - [3.2. Task 2 - Price Increase after Drop in 3 Days](#32-task-2---price-increase-after-drop-in-3-days)
- [4. Airflow](#4-airflow)
  - [4.1. Task 1 - Create DAG for Daily Data Download from Crypto API](#41-task-1---create-dag-for-daily-data-download-from-crypto-api)
  - [4.2. Task 2 - Adding Connection to PostgreSQL](#42-task-2---adding-connection-to-postgresql)
  - [4.3. Task 3 - Generate Graphs and Analysis](#43-task-3---generate-graphs-and-analysis)


# 0. Clone the code

First you will need to clone the code and change to the branch with the final version of the code

```
gh repo clone mutt-data-exams/exam-simon-bustamante
```
```
cd exam-simon-bustamante
```
```
git checkout simon
```

## 0.1. Pre requisites

### Install docker following the [official web site](https://docs.docker.com/desktop/install/ubuntu/)
### Install docker compose 
```
sudo apt install docker-compose
```


# 1. Getting crypto token data

Please be sure you are using Python3.10. This was the tested version 

## 1.1. Task 1 - Crypto Data Downloader

### Access the 1.-getting-crypto-token-data folder

```
cd 1.-getting-crypto-token-data
```

### Run the code by typing the command line

```
python crypto_data_downloader.py --date 2023-10-10 --coin-id bitcoin
```

## 1.2. Task 2 - Automation with CRON

### 1.2.1. Adding logging library to the code   

At this point the code has been updated by adding logging library

### 1.2.2. CRON Instructions to automate execution

Please run the following script.sh in Ubuntu 22.04 LTS. 
```
#!/bin/bash

# get current date YYYY-MM-DD
current_date=$(date +%Y-%m-%d)

/usr/bin/python3.10 /path/to/script/crypto_data_downloader.py --date $current_date --coin-id bitcoin && \
/usr/bin/python3.10 /path/to/script/crypto_data_downloader.py --date $current_date --coin-id ethereum && \
/usr/bin/python3.10 /path/to/script/crypto_data_downloader.py --date $current_date --coin-id cardano

```
Now run the following command
```
crontab -e
```
add the following line on the file

```
0 3 * * * path/to/script/script-to-cron.sh
```

Explanation: 

```
Minute: 0 - This field specifies the minute of the hour when the task will run. In this case, 0 means the task will run at the beginning of the hour, i.e., at 00 minutes.

Hour: 3 - This field specifies the hour of the day when the task will run. Here, 3 means the task will run at 3 AM.

Day of the Month: * - An asterisk in this field means that the task will run every day of the month. There's no restriction on the day.

Month: * - Just like the day of the month field, an asterisk in the month field indicates that there's no restriction on the month; the task will run every month.

Day of the Week: * - This field specifies the days of the week on which the task should run. An asterisk means there's no restriction on the day of the week; the task will run every day of the week.
```

## 1.3. Task 3 - Adding Bulk Processing Support

At this point it was necessary to specify args in a explicit way by command line:

* **--coin-id**: Identifier of the cryptocurrency (e.g., bitcoin)
* **--date**: Date in ISO8601 format (YYYY-MM-DD) for single day processing
* **--start-date**: Start date in ISO8601 format (YYYY-MM-DD) for bulk processing
* **--end-date**: End date in ISO8601 format (YYYY-MM-DD) for bulk processing

So the method **process_single_day()** will work in this way 

```
python3.10 crypto_data_downloader.py --date 2023-10-10 --coin-id bitcoin
```

And the method **process_bulk_days()** will work in this way

```
python3.10 crypto_data_downloader.py --start-date 2023-10-10 --end-date 2023-10-31 --coin-id bitcoin
```
### 1.3.1. Task 3 Bonus

There are 3 workers by default that uses the **process_single_day()** method. If you need to specify other quatity of workers for the script you can use the next parameter:

* **--workers**: Integer number like 3


# 2. Loading data into the database

## 2.1. Task 1 - Installing PostgreSQL with Two Tables

### 2.1.1. Enter the folder with the docker-compose.yml file

```
cd 2.-loading-data-into-db
```
### 2.1.2. Run the containers

```
docker-compose up -d
```

You will receive a feedback like this:
``````
Creating network "0-postgresql-docker_default" with the default driver
Creating 0-postgresql-docker_adminer_1 ... done
Creating 0-postgresql-docker_db_1      ... done
``````
### 2.1.3 Open browser on http://localhost:8080 to see a db called "simon" with two tables: 

* **coin_data**: Which contains the coin id, price in USD, date and a field that stores the whole API JSON response
* **coin_month_data**: Which contains coin id, the year and month and the maximum/minimum values for that period.

### 2.1.4. Verify Postgresql Ports

```
docker-compose ps
```

This will show something like this 

``````
           Name                           Command               State                    Ports                  
-----------------------------------------------------------------------------------------------------------------
2-loading-data-into-db_adminer_1   entrypoint.sh php -S [::]: ...   Up      0.0.0.0:8080->8080/tcp,:::8080->8080/tcp
2-loading-data-into-db_db_1        docker-entrypoint.sh postgres    Up      0.0.0.0:5432->5432/tcp,:::5432->5432/tcp
``````
It means that posgresql is on port 5432 and can be accessed by http on port 8080 with app adminer 


## 2.2. Task 2 - Enabling Data Storage on PostgreSQL

At this point you will be able to add in command line the parameter **--db** which allows to save and update the data on postgresql **coin_data** and **coin_month_data** 

example:
```
python3.10 crypto_data_downloader.py --date 2024-01-03 --coin-id bitcoin --db
```


# 3. Analysing coin data with SQL

## 3.1. Task 1 - Get the average price for each coin by month.

According context 2, a Postgresql database was deployed by using docker-compose

### 3.1.1. Access Docker container command line

According point 2.1.4. we need to access the container "2-loading-data-into-db_db_1"

```
docker exec -it 2-loading-data-into-db_db_1 bash
```

### 3.1.2. Access Postgresql by command line

```
psql -U simon
```

### 3.1.3 List all tables where "simon" is owner
```
simon=# \dt
```
This will show something like:
            List of relations
 Schema |      Name       | Type  | Owner 
--------+-----------------+-------+-------
 public | coin_data       | table | simon
 public | coin_month_data | table | simon
(2 rows)

### 3.1.4 Run the SQL Query to get average price for each coin by month.

```
SELECT coin,
       DATE_TRUNC('month', date) AS month,
       AVG(price) AS average_price
FROM coin_data
GROUP BY coin, DATE_TRUNC('month', date)
ORDER BY coin, month;
```
you will get a result similar to this:

``````
   coin   |         month          |   average_price    
----------+------------------------+--------------------
 bitcoin  | 2021-01-01 00:00:00+00 |  34634.24310969527
 bitcoin  | 2021-02-01 00:00:00+00 |  45897.94904982025
 bitcoin  | 2021-03-01 00:00:00+00 |  54532.80524870421
 bitcoin  | 2021-04-01 00:00:00+00 |  57148.23715053178
 bitcoin  | 2021-05-01 00:00:00+00 |  47187.71479020571
 bitcoin  | 2021-06-01 00:00:00+00 | 35973.744469242396
 bitcoin  | 2021-07-01 00:00:00+00 |  34271.52813871139
 bitcoin  | 2021-08-01 00:00:00+00 | 45563.673525567494
 bitcoin  | 2021-09-01 00:00:00+00 | 46085.361451894605
 bitcoin  | 2024-01-01 00:00:00+00 |  43790.51908331786
 cardano  | 2021-01-01 00:00:00+00 |  0.308016440509644
 cardano  | 2021-02-01 00:00:00+00 | 0.8315797076480568
 cardano  | 2021-03-01 00:00:00+00 | 1.1731643529399323
 cardano  | 2021-04-01 00:00:00+00 | 1.2524359430538148
 cardano  | 2021-05-01 00:00:00+00 | 1.6442684886829722
 cardano  | 2021-06-01 00:00:00+00 |  1.492185312749047
 cardano  | 2021-07-01 00:00:00+00 |  1.285418488380166
 cardano  | 2021-08-01 00:00:00+00 |  2.063806798270017
 cardano  | 2021-09-01 00:00:00+00 |   2.45556858739567
 ethereum | 2021-01-01 00:00:00+00 | 1183.8709533899446
 ethereum | 2021-02-01 00:00:00+00 |  1697.467398163695
 ethereum | 2021-03-01 00:00:00+00 | 1721.3937029088065
 ethereum | 2021-04-01 00:00:00+00 | 2267.6429867691145
 ethereum | 2021-05-01 00:00:00+00 |  3154.503868203675
 ethereum | 2021-06-01 00:00:00+00 | 2353.0047515800643
 ethereum | 2021-07-01 00:00:00+00 |  2126.662470111579
 ethereum | 2021-08-01 00:00:00+00 | 3070.1528767132772
 ethereum | 2021-09-01 00:00:00+00 |  3352.656358246009
(28 rows)
``````
## 3.2. Task 2 - Price Increase after Drop in 3 Days

### 3.2.1. Copy task2.sql to the container
```
docker cp task2/task2.sql 2-loading-data-into-db_db_1:/task2.sql
```

### 3.2.2. Access the container

```
docker exec -it 2-loading-data-into-db_db_1 bash
```

### 3.2.3. Run the script SQL task2.sql

```
psql -U simon -d simon -f task2.sql
```
You should see a result very similar to this

``````
   coin   |  average_increase   |   market_cap_usd   
----------+---------------------+--------------------
 bitcoin  |  1338.1402043940275 | 1187737045885.1743
 cardano  | 0.11433717672368067 |  95003730487.98029
 ethereum |  159.72501441156058 | 481380994613.09344
``````

# 4. Airflow

NOTE: Before you proceed down the last docker compose

```
docker-compose down
```

## 4.1. Task 1 - Create DAG for Daily Data Download from Crypto API

### 4.1.1. Install Airflow from community

* Create a airflow-orc folder in 4.-airflow folder

```
mkdir -p 4.-p airflow/airflow-orc
```
```
cd 4.-airflow/airflow-orc
```

* Download docker-compose.yml
```
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.8.1/docker-compose.yaml'
```
NOTE: Use the one added on this release 4.-airflow/docker-compose.yaml to avoid loading some default example that are not included on this test. Also this will include the conection to the new postgresql with airflow db.

* Set the Airflow user

```
mkdir -p ./dags ./logs ./plugins ./config
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

* Initialize Airflow DB and wait while the process is completed

```
docker compose up airflow-init
```

* Start the service

```
docker compose up
```

* Copy coin_data.sql to task1 folder (be sure you are on 4.-airflow/airflow-orc)

```
cp -r ../../2.-loading-data-into-db/init/ .
```

* Copy crypto_data_downloader_for_airflow.py to libs (be sure you are on 4.-airflow/airflow-orc)
```
cp ../../1.-getting-crypto-token-data/Task1/libs/crypto_data_downloader_for_airflow.py dags/libs/
```

* Copy dag_crypto_downloader.py

```
cp ./../1.-getting-crypto-token-data/Task1/dag_crypto_downloader.py dags/
```

NOTE: at this point crypto_data_downloader.py will require a change on the class **MainApplication**  specifically on the constructor. This class will be renamed like **MainApplicationForAirFlow**

```
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
```

### 4.1.2. Run the DAG related with Task1

If the source code is copied according the before steps you will be able to see the DAG **daily_data_downloader** on the list by accesing **http://localhost:8080/**  user: **airflow** pass:**airflow**.  Unpause the DAG and everything will ready. Optionally you can run the DAG manualy by pressing the Play icon on the DAG List.

## 4.2. Task 2 - Adding Connection to PostgreSQL

### 4.2.1. By Webserver

* Open airflow.cfg an enable Test by web browser

```
test_connection = Enabled
```

* Restart airflow

```
docker-compose stop
```
```
docker-compose up
```

* Browse to **Admin->Connection**
* Click on **+** Icon
* Set **Conn Id: postgres_stock_conn**
* Set **Conn Type: Postgres**
* Set **Host: postgres** NOTE: This is the name of postgres on the docker-compose stack
* Set **DB/Schema: airflow**
* Set **Login: airflow**
* Set **Password: airflow**
* Set **Port: 5432**
* Press **Test**
![Alt text](<Screenshot from 2024-01-21 11-17-45.png>)
* Press **Save**

### 4.2.2. By Command Line

* Copy Task2 test_conn_by_cli.py to container

```
docker cp test_conn_by_cli.py airflow-orc_airflow-worker_1:/opt/airflow/
```

* Access to the  worker container

```
docker exec -it airflow-orc_airflow-worker_1 bash
```

* Run airflow command line

```
airflow connections add 'postgres_stock_conn_cli' --conn-uri 'postgresql://airflow:airflow@postgres:5432/airflow'
```

* Test Connection

```
python test_conn_by_cli.py 
```

At this point you should see a message in the command line like 

``````
Connection to PostgreSQL was successful!
``````

## 4.3. Task 3 - Generate Graphs and Analysis


* Access to the  worker, scheduler, webserver and triggerer  container

```
docker exec -it airflow-orc_airflow-worker_1 bash
```

* Install Pandas y matplotlib, for each container

```
pip install matplotlib pandas
```

* Restart docker-compose

```
docker-compose stop
```
```
docker-compose up
```

* Copy the source code to dag folder

```
cd 4-airflow
```
```
cp -r Task3/* airflow-orc/dags/
```
NOTE: at this point the destination folder should have a list like this one: 

``````
ls -l dags/
total 12
-rw-rw-r-- 1 sabb sabb  874 ene 21 18:00 dag_crypto_downloader.py
-rw-rw-r-- 1 sabb sabb 1758 ene 21 17:59 dag_daily_data_downloader_and_plotter.py
drwxrwxr-x 3 sabb sabb 4096 ene 21 17:59 libs
``````
``````
ls -l dags/libs/
total 16
-rw-rw-r-- 1 sabb sabb 1876 ene 21 17:59 crypto_analysis.py
-rw-rw-r-- 1 sabb sabb 7646 ene 21 17:59 crypto_data_downloader_for_airflow.py
``````

* Run manually the DAG from Web Browser or Start it by CLI

```
docker exec -it airflow-orc_airflow-worker_1 bash
```
```
airflow dags trigger daily_data_downloader_and_plotter
```

* Exit Container

```
exit 
```

* Open the plot the next path:

```
ls 4.-airflow/airflow-orc/bitcoin_prices_during_30_days_<YOUR-DATE>.png 
```

* Verify the **The average difference** in price for the last 30 days in next logged path:

```
ls 4.-airflow/airflow-orc/logs/dag_id\=daily_data_downloader_and_plotter/run_id\=manual__<YOUR-DATE>/task_id\=plot_and_calculate/attempt\=1.log 
```
``````
Note: open the file and you will see a message very similar to this:

INFO - The average difference in price for the last 30 days is: 81.98582453817804
``````


THANK YOU VERY MUCH!!!