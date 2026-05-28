# -sms-api-stress-test-
Bir SMS API'sini stress (yük) testi
Gerekli Kütüphanelerin Kurulumu
​Öncelikle asenkron HTTP istekleri için aiohttp kütüphanesini yüklemelisin:

pip install aiohttp

Python sms_stress_test.py

1. Gerçek Operatör Maliyetleri: Eğer testi entegratör firmanın (İleti Merkezi, Netgsm, Verimor vb.) canlı (production) API url'i üzerinde yaparsan, gönderdiğin her başarılı istek bakiyenden düşebilir veya gerçek kişilere SMS olarak gidebilir. Testi firmanın sağladığı Sandbox/Test ortamı URL'i ile yapmaya özen göster.
