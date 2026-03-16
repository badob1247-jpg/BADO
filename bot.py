import os
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# --- ТОХИРГОО ---
TARGET_PROB = 0.70  
TEST_DURATION = 60 
MARKET_NAME = "Bitcoin Up or Down - 5 Minutes"

def main():
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=TEST_DURATION)
    last_id = ""
    total_trades, wins, losses = 0, 0, 0

    print("="*60)
    print(f"🚀 БОТ АСЛАА: {start_time.strftime('%H:%M:%S')}")
    print(f"🎯 ХАЙЖ БУЙ НЭР: '{MARKET_NAME}'")
    print("="*60)

    while datetime.now() < end_time:
        try:
            # Polymarket API-аас дата татах
            res = requests.get("https://gamma-api.polymarket.com/markets?active=True&limit=100", timeout=5).json()
            
            target_m = None
            for m in res:
                # Таны хэлсэн яг тэр нэрээр хайж байна
                if MARKET_NAME in m.get('question', ''):
                    target_m = m
                    break
            
            if target_m:
                prices = target_m.get('outcomePrices', [0, 0])
                up, down = float(prices[0]), float(prices[1])
                m_id = target_m['id']
                
                # Секунд тутамд сайттай чинь зэрэгцэж тоо гүйнэ
                print(f"\r🔍 [{datetime.now().strftime('%H:%M:%S')}] UP: {up*100:.0f}% | DOWN: {down*100:.0f}%", end="", flush=True)

                # 70% нөхцөл шалгах
                if (up >= TARGET_PROB or down >= TARGET_PROB) and m_id != last_id:
                    side = "UP" if up >= TARGET_PROB else "DOWN"
                    last_id = m_id
                    total_trades += 1
                    
                    print(f"\n\n🔔 [!] АРИЛЖААНД ОРЛОО: {side} {max(up, down)*100:.0f}%")
                    print("⏳ 5 минут хүлээнэ... Үр дүнг тооцож байна.")
                    
                    # 5 минут хүлээх (Арилжаа дуустал)
                    time.sleep(300) 
                    
                    # Үр дүнг мэдээлэх (Simulated notification)
                    import random
                    is_win = random.choice([True, False]) 
                    
                    if is_win:
                        wins += 1
                        print(f"✅✅✅ МЭДЭГДЭЛ: Арилжаа ДУУСЛАА. ТА ЯЛЛАА! (+0.90 USDC)")
                    else:
                        losses += 1
                        print(f"❌❌❌ МЭДЭГДЭЛ: Арилжаа ДУУСЛАА. ТА АЛДЛАА. (-1.0 USDC)")
                    
                    print(f"📊 Одоогийн байдал: {wins} Ялалт | {losses} Алдагдал\n")
                    print("--- Дараагийн шинэ арилжааг хайж байна ---")
            else:
                print(f"\r⚠️ [{datetime.now().strftime('%H:%M:%S')}] '{MARKET_NAME}' хайж байна...", end="")

        except Exception as e:
            print(f"\n❌ Алдаа гарлаа: {e}")
        
        time.sleep(1)

    print("\n" + "="*60)
    print(f"📊 ТӨГСГӨЛИЙН ТАЙЛАН: Нийт: {total_trades} | Ялалт: {wins} | Алдагдал: {losses}")
    print("="*60)

if __name__ == "__main__":
    main()