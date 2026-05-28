import asyncio
import time
import aiohttp

# --- YAPILANDIRMA (Buraları kendi API'ne göre düzenle) ---
API_URL = "https://api.sms-servisiniz.com/v1/send"  # Test edilecek API uç noktası
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer KENDI_API_ANAHTARINIZ"  # Varsa API Token
}

# Örnek SMS Gönderim Payload'u
PAYLOAD_TEMPLATE = {
    "sender": "TEST_REKLAM",
    "message": "Bu bir SMS API stress test mesajıdır.",
    "phone": "5551112233"
}

TOTAL_REQUESTS = 500  # Toplamda gönderilecek istek sayısı
CONCURRENT_REQUESTS = 50  # Aynı anda (eşzamanlı) çalışacak istek sayısı
# --------------------------------------------------------

async def send_sms_request(session, request_id, stats):
    """Tek bir SMS API isteği gönderir ve sonucunu kaydeder."""
    start_time = time.time()
    try:
        async with session.post(API_URL, json=PAYLOAD_TEMPLATE, headers=HEADERS, timeout=10) as response:
            latency = (time.time() - start_time) * 1000  # ms cinsinden gecikme
            
            if response.status == 200 or response.status == 201:
                stats["success"] += 1
            else:
                stats["failed"] += 1
                stats["errors"][response.status] = stats["errors"].get(response.status, 0) + 1
            
            stats["latencies"].append(latency)
            
    except asyncio.TimeoutError:
        stats["failed"] += 1
        stats["errors"]["Timeout"] = stats["errors"].get("Timeout", 0) + 1
    except Exception as e:
        stats["failed"] += 1
        error_name = type(e).__name__
        stats["errors"][error_name] = stats["errors"].get(error_name, 0) + 1

async def worker(queue, session, stats):
    """Kuyruktan görevleri alıp sırayla çalıştıran işçi fonksiyonu."""
    while True:
        request_id = await queue.get()
        if request_id is None:
            queue.task_done()
            break
        await send_sms_request(session, request_id, stats)
        queue.task_done()

async def main():
    # Test istatistiklerini tutacağımız sözlük
    stats = {
        "success": 0,
        "failed": 0,
        "latencies": [],
        "errors": {}
    }
    
    queue = asyncio.Queue()
    
    # Kuyruğa toplam istek sayısı kadar görev ekliyoruz
    for i in range(TOTAL_REQUESTS):
        await queue.put(i)
        
    # İşçilerin durması için kuyruğun sonuna 'None' (bitiş işareti) ekliyoruz
    for _ in range(CONCURRENT_REQUESTS):
        await queue.put(None)

    print(f"🚀 Stress Test Başlatılıyor...")
    print(f"📊 Toplam İstek: {TOTAL_REQUESTS} | Eşzamanlı İstek (Concurrency): {CONCURRENT_REQUESTS}\n")
    
    start_test_time = time.time()
    
    # Asenkron HTTP oturumu başlatma
    async with aiohttp.ClientSession() as session:
        # Belirttiğimiz eşzamanlılık (concurrency) sayısı kadar işçi (worker) başlatıyoruz
        tasks = []
        for _ in range(CONCURRENT_REQUESTS):
            task = asyncio.create_task(worker(queue, session, stats))
            tasks.append(task)
            
        # Tüm görevlerin (kuyruğun) bitmesini bekle
        await queue.join()
        await asyncio.gather(*tasks)

    end_test_time = time.time()
    total_duration = end_test_time - start_test_time

    # --- RAPORLAMA ---
    print("=" * 40)
    print("🏁 TEST SONUÇLARI RAPORU")
    print("=" * 40)
    print(f"⏱️ Toplam Geçen Süre   : {total_duration:.2f} saniye")
    print(f"📈 Saniyedeki İstek (RPS): {TOTAL_REQUESTS / total_duration:.2f}")
    print(f"✅ Başarılı İstek     : {stats['success']}")
    print(f"❌ Başarısız İstek    : {stats['failed']}")
    
    if stats["latencies"]:
        avg_latency = sum(stats["latencies"]) / len(stats["latencies"])
        max_latency = max(stats["latencies"])
        min_latency = min(stats["latencies"])
        print(f"⚡ Ortalama Yanıt Süresi: {avg_latency:.2f} ms")
        print(f"⚡ En Yavaş Yanıt       : {max_latency:.2f} ms")
        print(f"⚡ En Hızlı Yanıt       : {min_latency:.2f} ms")
        
    if stats["errors"]:
        print("\n⚠️ Alınan Hata Detayları (Durum Kodları):")
        for code, count in stats["errors"].items():
            print(f"   • {code}: {count} adet")
    print("=" * 40)

if __name__ == "__main__":
    # Python 3.7+ için asenkron döngüyü çalıştırır
    asyncio.run(main())
