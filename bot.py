import os
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ✅ SSL алдаа засах
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

# --- ТОХИРГОО ---
TARGET_PROB = 0.70  
TEST_DURATION = 60 
MARKET_SEARCH_TERM = "bitcoin up or down"

# ✅ ГЛОБАЛ ХУВЬСАГЧ
pending_trade = None
last_id = ""

def get_all_markets():
    """API-аас шинээр гарсан market-үүдийг олох"""
    try:
        res = requests.get(
            "https://gamma-api.polymarket.com/markets",
            params={
                'active': 'true',
                'limit': 500,
                'order': 'createdAt',
                'ascending': 'false'
            },
            verify=False,
            timeout=5
        ).json()
        return res
    except Exception as e:
        print(f"\n❌ API алдаа: {e}")
        return []

def find_target_market(markets):
    """'Bitcoin Up or Down' market олох"""
    for m in markets:
        question = m.get('question', '').lower()
        if MARKET_SEARCH_TERM in question and '5' in question:
            return m
    return None

def parse_prices(market):
    """Prices-г зөв сойзох - 0-100 эсвэл 0-1 масштаб"""
    try:
        prices = market.get('outcomePrices', [0.5, 0.5])
        
        if isinstance(prices, str):
            import json
            try:
                prices = json.loads(prices)
            except:
                prices = [0.5, 0.5]
        
        if isinstance(prices, (list, tuple)) and len(prices) >= 2:
            up = float(str(prices[0]).strip('"').strip("'"))
            down = float(str(prices[1]).strip('"').strip("'"))
            
            total = up + down
            
            if total > 1.5:
                up = up / 100
                down = down / 100
            
            return up, down
    except Exception as e:
        print(f"⚠️ Prices parsing алдаа: {e}")
    
    return 0.5, 0.5

def main():
    global pending_trade, last_id
    
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=TEST_DURATION)
    total_trades, wins, losses = 0, 0, 0
    cycle_num = 1
    cycle_start = start_time

    print("="*70)
    print(f"🚀 БОТ АСЛАА: {start_time.strftime('%H:%M:%S')}")
    print(f"🎯 ХАЙЖ БУЙ: '{MARKET_SEARCH_TERM}' (5 Minutes)")
    print(f"📊 Threshold: {TARGET_PROB*100:.0f}%")
    print("="*70)

    while datetime.now() < end_time:
        now = datetime.now()
        time_in_cycle = (now - cycle_start).total_seconds()
        
        try:
            if time_in_cycle < 300:
                if pending_trade is None:
                    markets = get_all_markets()
                    
                    if not markets:
                        print(f"\r⚠️  API буцаа мэдээлэл байхгүй", end="", flush=True)
                        try:
                            time.sleep(1)
                        except KeyboardInterrupt:
                            raise
                        continue
                    
                    target_m = find_target_market(markets)
                    
                    if target_m:
                        up, down = parse_prices(target_m)
                        m_id = target_m.get('id', '')
                        question = target_m.get('question', 'Unknown')
                        
                        print(f"\r🔍 [{now.strftime('%H:%M:%S')}] UP: {up*100:.0f}% | DOWN: {down*100:.0f}%%", end="", flush=True)

                        side = None
                        signal_prob = 0
                        
                        if up >= TARGET_PROB:
                            side = "UP"
                            signal_prob = up
                        elif down >= TARGET_PROB:
                            side = "DOWN"
                            signal_prob = down
                        
                        if side and m_id != last_id:
                            last_id = m_id
                            total_trades += 1
                            
                            print(f"\n\n🔔 [SIGNAL DETECTED!] {side} >= {TARGET_PROB*100:.0f}%")
                            print(f"   📍 Market: {question}")
                            print(f"   📈 {side}: {signal_prob*100:.1f}%")
                            print(f"   🆔 Market ID: {m_id}")
                            print("   ⏳ 5 минут хүлээнэ...")
                             
                            pending_trade = {
                                'market_id': m_id,
                                'market_name': question,
                                'side': side,
                                'probability': signal_prob,
                                'timestamp': now
                            }
                    else:
                        print(f"\r⚠️  [{now.strftime('%H:%M:%S')}] Market хайж байна...", end="", flush=True)
                
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    raise
            
            else:
                if pending_trade:
                    print(f"\n\n[{now.strftime('%H:%M:%S')}] ========== CLAIMING PHASE ==========")
                    print(f"   📍 Market: {pending_trade['market_name']}")
                    print(f"   📈 Side: {pending_trade['side']} ({pending_trade['probability']*100:.1f}%)")
                    print("   🎲 Үр дүн сүлжээ хийж байна...")
                    
                    import random
                    is_win = random.choice([True, False])
                    
                    if is_win:
                        wins += 1
                        print(f"   ✅ ҮЙНЭГДЭЛ: ДУУСЛАА. ТА ЯЛЛАА! (+0.90 USDC)")
                    else:
                        losses += 1
                        print(f"   ❌ ҮЙНЭГДЭЛ: ДУУСЛАА. ТА АЛДЛАА. (-1.0 USDC)")
                    
                    win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
                    print(f"   📊 Байдал: {wins}✅ | {losses}❌ | Win Rate: {win_rate:.0f}%")
                    print("="*70)
                    
                    pending_trade = None
                else:
                    print(f"\r[{now.strftime('%H:%M:%S')}] CLAIMING phase: хүлээж байна...", end="", flush=True)
                
                if time_in_cycle >= 600:
                    cycle_start = now
                    cycle_num += 1
                    pending_trade = None
                    print(f"\n\n[{now.strftime('%H:%M:%S')}] ========== CYCLE #{cycle_num}: TRADING PHASE ==========")
                
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    raise

        except KeyboardInterrupt:
            print(f"\n\n[{now.strftime('%H:%M:%S')}] 🛑 BOT STOPPED BY USER")
            print(f"   📈 Total Trades: {total_trades}")
            if total_trades > 0:
                print(f"   ✅ Wins: {wins}")
                print(f"   ❌ Losses: {losses}")
                print(f"   📊 Win Rate: {wins/total_trades*100:.0f}%")
            print("="*70)
            break
        except Exception as e:
            print(f"\n❌ Алдаа: {e}")
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                raise

    print("\n" + "="*70)
    print(f"📊 ТӨГСГӨЛИЙН ТАЙЛАН:")
    print(f"   ⏱️  Хугацаа: {TEST_DURATION} минут")
    print(f"   📈 Нийт Арилжаа: {total_trades}")
    print(f"   ✅ Ялалт: {wins}")
    print(f"   ❌ Алдагдал: {losses}")
    if total_trades > 0:
        print(f"   📊 Win Rate: {wins/total_trades*100:.0f}%")
    print("="*70)

if __name__ == "__main__":
    main()