# Proje: ACO-TR-LOGISTICS

Bu proje, Karınca Kolonisi Optimizasyonu (ACO) algoritmasının arkasındaki mantığı anlamak ve gerçek dünya verileriyle denemek için kişisel bir hevesle geliştirilmiştir.

Basit bir Gezgin Satıcı Problemi (TSP) olarak başlayan bu serüven, zamanla kapasite kısıtlamaları, çoklu araç filoları, zaman pencereleri ve hizmet süreleri gibi gerçek dünya kısıtlarını modelleyebilen kapsamlı bir VRP çözüm aracına dönüşmüştür.

Proje, yüksek performanslı rota hesaplamaları için **Docker üzerinde çalışan yerel bir OSRM sunucusu** kullanır. **Elitist Ant System (EAS)** ve daha gelişmiş **Max-Min Ant System (MMAS)** gibi birden fazla ACO stratejisini destekler ve performansı sistematik olarak analiz etmek için bir altyapı içerir.

Geliştirme sürecinde, bir yol arkadaşı olarak güncel yapay zeka araçlarından da faydalanılmıştır.

## Kurulum

Projenin çalışabilmesi için önce yerel rota sunucusunun kurulması, ardından Python ortamının ayarlanması gerekmektedir.

### Adım 1: OSRM Rota Sunucusunu Kurma (Sadece İlk Kurulumda)

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

# 4. Docker ile veriyi işleyin (Bu adımlar uzun sürebilir)
docker run -t -v "$(pwd)/osrm_data:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/turkey-latest.osm.pbf
docker run -t -v "$(pwd)/osrm_data:/data" osrm/osrm-backend osrm-partition /data/turkey-latest.osrm
docker run -t -v "$(pwd)/osrm_data:/data" osrm/osrm-backend osrm-customize /data/turkey-latest.osrm

# 5. OSRM Rota Sunucusunu arkaplanda başlatın
docker run -d -p 5000:5000 -v "$(pwd)/osrm_data:/data" osrm/osrm-backend osrm-routed --algorithm mld --max-table-size 8000 /data/turkey-latest.osrm
```
### Adım 2: Python Ortamını Ayarlama

```bash
# Sanal ortamı kur ve aktif et (macOS/Linux)
python3 -m venv .venv
source .venv/bin/activate

# Gerekli kütüphaneleri yükle
pip install -r requirements.txt
```

## Kullanım

Projenin iki ana kullanım modu vardır: tek bir optimizasyon çalıştırma veya sistematik deneyler yapma.

### Tek Bir Optimizasyon Çalıştırma
config.yaml dosyasındaki mevcut ayarlarla tek bir optimizasyon örneği çalıştırmak için:
```bash
python -m src.main
```
EAS ve MMAS arasında geçiş yapmak için config.yaml dosyasındaki aco bölümünde bulunan strategy anahtarını değiştirebilirsiniz.

```bash
# Akıllı durak seçimi (DBSCAN) stratejisini çalıştır
python -m src.main --strategy dbscan

# Farklı bir senaryo dosyasını çalıştır
python -m src.main --scenario data/scenarios/corlu_merkez_15_durak.json
```
### Sistematik Deneyler Çalıştırma
Farklı parametrelerin ve stratejilerin performansını karşılaştırmak için run_experiments.py script'ini kullanabilirsiniz. Bu script, parameter_grid içinde tanımlanan her bir konfigürasyonu birden çok kez çalıştırır ve sonuçları bir .csv dosyasına kaydeder.
```bash
python run_experiments.py
```
### Çıktılar
- *.html: Rotaların gösterildiği interaktif harita.
- *_convergence.png: Optimizasyonun iterasyonlara göre en iyi maliyeti nasıl düşürdüğünü gösteren yakınsama grafiği.
- experiment_results_*.csv: run_experiments.py tarafından oluşturulan detaylı deney sonuçları.

### Testleri Çalıştırma
Projenin temel bileşenlerinin doğru çalıştığını doğrulamak için:
```bash
pytest
```
Not: Testler, çalışan bir OSRM sunucusu gerektirmez.

## Lisans
Bu proje MIT Lisansı ile lisanslanmıştır.