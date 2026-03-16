import os
from web3 import Web3
from dotenv import load_dotenv

# .env файлаас мэдээллийг унших
load_dotenv()

# Polygon сүлжээнд холбогдох
w3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))

def start_check():
    pk = os.getenv("PK")
    try:
        # Private key-ээс хэтэвчний хаягийг гаргах
        account = w3.eth.account.from_key(pk)
        print("\n" + "="*30)
        print(f"ХОЛБОЛТ АМЖИЛТТАЙ!")
        print(f"Таны хаяг: {account.address}")
        
        # Дансны үлдэгдэл шалгах
        balance = w3.eth.get_balance(account.address)
        matic_amount = w3.from_wei(balance, 'ether')
        print(f"Үлдэгдэл: {matic_amount} MATIC")
        print("="*30 + "\n")
    except Exception as e:
        print(f"\nАлдаа: {e}")
        print("Зөвлөгөө: .env файл дотор PK= гэж бичээд хадгалсан уу?\n")

start_check()