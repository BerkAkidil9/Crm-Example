#!/usr/bin/env python
"""
Script to verify .env DB settings and test PostgreSQL connection.
Run from project root: python check_db_connection.py
"""
import os
import sys
from pathlib import Path

# Same as Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env', override=True)

db_user = os.getenv('DB_USER', '')
db_password = os.getenv('DB_PASSWORD', '')
db_name = os.getenv('DB_NAME', '')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')

print('=== .env\'den okunan DB bilgileri ===')
print(f'DB_USER     : {repr(db_user)} (uzunluk: {len(db_user)})')
print(f'DB_PASSWORD : {repr(db_password)} (uzunluk: {len(db_password)})')
print(f'DB_NAME     : {repr(db_name)}')
print(f'DB_HOST     : {db_host}:{db_port}')
print()

if not db_user or not db_password or not db_name:
    print('HATA: DB_USER, DB_PASSWORD veya DB_NAME bos. .env dosyasini kontrol et.')
    sys.exit(1)

print('PostgreSQL baglantisi deneniyor...')
try:
    import psycopg
    conn = psycopg.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password,
    )
    conn.close()
    print('BAGLANTI BASARILI. .env ile PostgreSQL uyumlu.')
except Exception as e:
    print(f'BAGLANTI HATASI: {e}')
    print()
    print('Yapilacaklar:')
    print('1. PostgreSQL\'de postgres ile baglan.')
    print('2. Sifreyi .env ile AYNI yap:')
    print(f'   ALTER USER {db_user.lower()} WITH PASSWORD {repr(db_password)};')
    print('3. Bu scripti tekrar calistir.')
    sys.exit(1)
