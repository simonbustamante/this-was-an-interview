from airflow.providers.postgres.hooks.postgres import PostgresHook

def test_postgres():
    hook = PostgresHook(postgres_conn_id='postgres_stock_conn_cli')
    try:
        connection = hook.get_conn()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        print("Connection to PostgreSQL was successful!")
    except Exception as e:
        print(f"An error occurred: {e}")

test_postgres()
