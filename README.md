# Visualisasi Revenue 📊 - 

## Airflow Kibana Elastic_search
Repositori ini berisi proyek visualisasi data menggunakan Apache Airflow , Elastic_search, dan Kibana. Penggunaan Airflow untuk otomatisasi step dan kemudian kita memakai elastic search 
untuk menyimpan data kita serta menggunakan kibana untuk visualisasi dan mendapatkan insight dari dataset yang kita miliki. 

## Daftar Isi 🗒️

Link Terkait Project
Project Overview
Metode yang Digunakan
File yang Tersedia
Cara Menggunakan Project Ini
Dependencies
Libraries
Author

## Link Terkait Project ⛓️‍💥
[LINK_DATASET](https://www.kaggle.com/datasets/sadiqshah/bike-sales-in-europe/data)

## Project Overview 📝

Dalam proyek ini, saya menggunakan Apache Airflow untuk mengautomasi proses ETL (Extract, Transform, Load) dan menggunakan Kibana untuk visualisasi data yang telah diproses.
Beberapa langkah utama yang dicakup dalam proyek ini adalah:

Pengaturan Airflow:

Mengonfigurasi dan menjalankan Airflow untuk mengelola alur kerja. Kita set di waktu tertentu kapan airflow akan mengambil dataset secara otomatis kemudian kita masukkan ke SQL setelah itu dari SQL kita coba transfer data kita ke Elastic Search. 

Pengembangan DAG:

Membangun DAG (Directed Acyclic Graph) untuk mendefinisikan alur kerja data.

Transformasi Data:

Melakukan transformasi data yang diperlukan sebelum visualisasi.
Visualisasi dengan Kibana:

Menggunakan Kibana untuk menyajikan data dalam format yang dapat dianalisis secara visual.

## Metode yang Digunakan 🛠️

ETL (Extract, Transform, Load)
Visualisasi Data
Automasi Proses

## File yang Tersedia 📂

Maulana_Achsan_DAG.py

 Skrip Python yang berisi definisi DAG di Airflow, termasuk langkah-langkah dalam proses ETL.

great_expectations.ipynb

Jupyter Notebook yang berisi validasi data menggunakan Great Expectations.

(folder) images: Hasil visualisasi dari Kibana.

Terdapat juga hasil dari data raw dan data clean pada github ini untuk melihat datasetnya. 


## Cara Menggunakan Project Ini 💻
Clone repositori ini ke dalam lokal Anda.

git clone https://github.com/asanmaulana/visualization_kibana_elastic

Jalankan Apache Airflow untuk mengelola alur kerja.

airflow webserver --port 8080

airflow scheduler

Jalankan DAG di Airflow untuk memulai proses ETL.

Akses Kibana untuk melihat visualisasi data.

## Dependencies ⚙️
Python 3.9.19
Apache Airflow

## Libraries 📚

Apache Airflow
Pandas
NumPy
Elasticsearch
Kibana
Datetime

## Author ✍️
Maulana Achsan

