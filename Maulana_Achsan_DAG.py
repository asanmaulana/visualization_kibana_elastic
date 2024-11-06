import pandas as pd
import psycopg2 as db
import datetime as dt
from datetime import timedelta
from io import StringIO
from pytz import timezone

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# memasukkan data ke postgres menggunakan docker 

def save_to_sql():

    conn_string = "dbname='postgres' host='postgres' user='airflow' password='airflow'"
    conn = db.connect(conn_string)
    cur = conn.cursor()

    # Membuat tabel jika belum ada
    sql = '''
        CREATE TABLE IF NOT EXISTS table_m3 (
            "Date" DATE,
            "Day" INT,
            "Month" VARCHAR(50),
            "Year" INT,
            "Customer_Age" INT,
            "Age_Group" VARCHAR(50),
            "Customer_Gender" CHAR(1),
            "Country" VARCHAR(100),
            "State" VARCHAR(100),
            "Product_Category" VARCHAR(100),
            "Sub_Category" VARCHAR(100),
            "Product" VARCHAR(255),
            "Order_Quantity" INT,
            "Unit_Cost" NUMERIC,
            "Unit_Price" NUMERIC,
            "Profit" NUMERIC,
            "Cost" NUMERIC,
            "Revenue" NUMERIC
        );
    '''
    cur.execute(sql)
    conn.commit()
    cur.execute("DELETE FROM table_m3") # menghapus jika masih ada file di dalam sql ditakutkan nanti double copy dengan dag atau db sebelumnya
                                        # karena kita hanya mengulang file yang sama. di real life mungkin penamaan database aja atau table yang beda
                                        
    # Baca file CSV menggunakan pandas
    df = pd.read_csv('/opt/airflow/dags/P2M3_maulana_achsan_data_raw.csv')

    # Buat StringIO buffer untuk mempersiapkan data sebelum di-copy ke PostgreSQL
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False)  # Convert DataFrame ke CSV format, tanpa index dan header
    buffer.seek(0)

    # Menggunakan COPY untuk mengimpor semua data
    cur.copy_expert("""
        COPY table_m3 ("Date", "Day", "Month", "Year", "Customer_Age", "Age_Group", 
                       "Customer_Gender", "Country", "State", "Product_Category", 
                       "Sub_Category", "Product", "Order_Quantity", "Unit_Cost", 
                       "Unit_Price", "Profit", "Cost", "Revenue") 
        FROM STDIN WITH CSV;
    """, buffer)

    # Commit and close the connection
    conn.commit()
    cur.close()
    conn.close()

# ambil data dan cleaning data 
def fetch_and_clean_data():
    conn_string = "dbname='postgres' host='postgres' user='airflow' password='airflow'"
    conn = db.connect(conn_string)
    query = "SELECT * FROM table_m3;"
    
    # Ambil data dari PostgreSQL
    df = pd.read_sql(query, conn)
    conn.close()

    # Ekstra 1 kolom baru order_id dan diurutkankolom id

    df['order_id'] = (pd.Series(range(1, len(df) + 1)).astype(str) +  # Nomor urut
                        df['Country'].str[:3] # Mengambil 3 huruf pertama dari negara
                        + df['State'].str[:3]) # Mengambil 3 huruf pertama dari state

    # Memindahkan kolom 'order_id' ke urutan pertama
    cols = ['order_id'] + [col for col in df.columns if col != 'order_id']
    df = df[cols]

    ###### Data CLEANING ####

    # 1. Hapus data duplikat
    df = df.drop_duplicates()

    # 2. Normalisasi nama kolom
    df.columns = df.columns.str.strip()  # Menghapus spasi/tab di awal/akhir nama kolom
    df.columns = df.columns.str.lower()  # Mengubah semua menjadi lowercase
    df.columns = df.columns.str.replace(' ', '_')  # Mengganti spasi dengan underscore
    df.columns = df.columns.str.replace(r'\W', '', regex=True)  # Menghapus simbol yang tidak diperlukan

    # 3. Handling missing values
    for column in df.columns:
        if df[column].dtype == 'float64' or df[column].dtype == 'int64':
            df[column].fillna(df[column].median(), inplace=True)
        else:
            df[column].fillna('Unknown', inplace=True)
    
    

    # Simpan data yang sudah dibersihkan ke file CSV
    df.to_csv('/opt/airflow/dags/P2M3_maulana_achsan_data_clean.csv', index=False)



def send_to_elastic():
    es = Elasticsearch([{'host': 'elasticsearch', 'port': 9200}])
    df = pd.read_csv('/opt/airflow/dags/P2M3_maulana_achsan_data_clean.csv')

    # Membuat list of actions untuk bulk indexing
    actions = [
        {
            "_index": "milestone",  # Nama indeks di Elasticsearch
            "_source": r.to_dict()        # Konversi setiap baris ke dictionary
        }
        for _, r in df.iterrows()         # Iterasi melalui setiap baris di DataFrame
    ]

    # Melakukan bulk indexing
    bulk(es, actions)
    print(f"Sukses mengindeks {len(actions)} dokumen ke Elasticsearch.")





#################_______________________DAG_____________________________________#########

# Pengaturan DAG
default_args = {
    'owner': 'asan',
    'start_date': dt.datetime(2024, 10, 11, tzinfo=timezone('Asia/Jakarta')),
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}

with DAG('m3_dag_asan',
         default_args=default_args,
         schedule_interval='30 6 * * *',
         catchup=False
         ) as dag:

    print_starting = BashOperator(task_id='starting',
                                  bash_command='echo "I am reading the CSV now....."')

    csvSQL = PythonOperator(task_id='csv_to_SQL',
                             python_callable=save_to_sql)
    
    fetch_clean = PythonOperator(task_id='fetch_n_clean', 
                                 python_callable=fetch_and_clean_data)
    
    from_csv_to_elastic = PythonOperator(task_id = 'to_elastic_fr_csv',
                                         python_callable = send_to_elastic)

print_starting >> csvSQL >> fetch_clean >> from_csv_to_elastic
