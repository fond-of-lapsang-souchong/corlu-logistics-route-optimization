# Proje: ACO-TR-LOGISTICS

Bu proje, Karınca Kolonisi Optimizasyonu (ACO) algoritmasının arkasındaki mantığı anlamak ve gerçek dünya verileriyle denemek için kişisel bir hevesle geliştirilmiştir.

Basit bir Gezgin Satıcı Problemi (TSP) olarak başlayan bu serüven, zamanla kapasite kısıtlamaları ve çoklu araçları yönetebilen bir Araç Rotalama Problemi (VRP) çözüm aracına dönüştü. Proje, yüksek performanslı rota hesaplamaları için **Docker üzerinde çalışan yerel bir OSRM (Open Source Routing Machine) sunucusu** kullanacak şekilde geliştirilmiştir.

Geliştirme sürecinde, bir yol arkadaşı olarak güncel yapay zeka araçlarından da faydalanılmıştır.

## Kurulum ve İlk Çalıştırma

Projenin çalışabilmesi için önce yerel rota sunucusunun kurulması, ardından Python ortamının ayarlanması gerekmektedir.

### Adım 1: OSRM Rota Sunucusunu Kurma (Sadece İlk Kurulumda)

Bu proje, rota mesafelerini ve sürelerini milisaniyeler içinde hesaplamak için Docker üzerinde çalışan OSRM'i kullanır.

**Ön Gereksinim:**
*   [Docker](https://www.docker.com/) sisteminizde kurulu ve çalışır durumda olmalıdır.

**OSRM Kurulum Komutları:**

```bash
# 1. Projeyi bilgisayarınıza indirin ve klasörüne gidin
git clone https://github.com/fond-of-lapsang-souchong/ACO-TR-LOGISTICS.git
cd ACO-TR-LOGISTICS

# 2. OSRM için veri klasörü oluşturun
mkdir osrm_data

# 3. Türkiye harita verisini indirin
wget -P ./osrm_data https://download.geofabrik.de/europe/turkey-latest.osm.pbf

# 4. Docker ile veriyi işleyin
docker run -t -v "$(pwd)/osrm_data:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/turkey-latest.osm.pbf
docker run -t -v "$(pwd)/osrm_data:/data" osrm/osrm-backend osrm-partition /data/turkey-latest.osrm
docker run -t -v "$(pwd)/osrm_data:/data" osrm/osrm-backend osrm-customize /data/turkey-latest.osrm

# 5. OSRM Rota Sunucusunu arkaplanda başlatın
docker run -d -p 5000:5000 -v "$(pwd)/osrm_data:/data" osrm/osrm-backend osrm-routed --algorithm mld --max-table-size 8000 /data/turkey-latest.osrm
```

### Adım 2: Python Ortamını Ayarlama

OSRM sunucusu arkaplanda çalışmaya başladıktan sonra Python ortamını kurabilirsiniz.

```bash
# Sanal ortamı kur ve aktif et (macOS/Linux)
python3 -m venv .venv
source .venv/bin/activate

# Gerekli kütüphaneleri yükle
pip install -r requirements.txt
```

## Projeyi Çalıştırma

Tüm kurulum adımları tamamlandıktan ve OSRM sunucusu arkaplanda çalışırken, projeyi aşağıdaki komutlarla çalıştırabilirsiniz.

```bash
# config.yaml'daki varsayılan senaryo ve filo ile çalıştır
python -m src.main

# Akıllı durak seçimi (DBSCAN) stratejisini çalıştır
python -m src.main --strategy dbscan

# Farklı bir senaryo dosyasını çalıştır
python -m src.main --scenario data/scenarios/corlu_merkez_15_durak.json
```
İşlem bitince, sonuç haritası projenin ana dizininde `.html` uzantısıyla oluşturulacaktır. Tüm varsayılan ayarlar (araç filosu, optimizasyon parametreleri vb.) için `config.yaml` dosyasına göz atabilirsin.

### Testleri Çalıştırma
Projenin temel bileşenlerinin doğru çalıştığını doğrulamak için:```bash
pytest
```
*Not: Testler, OSRM sunucusunun çalışmasını gerektirmeyen birim testleridir.*

## Lisans
Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.