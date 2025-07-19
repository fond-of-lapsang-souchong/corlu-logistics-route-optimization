# Proje: ACO-TR-LOGISTICS

Bu proje, Karınca Kolonisi Optimizasyonu (ACO) algoritmasının arkasındaki mantığı anlamak ve gerçek dünya verileriyle denemek için kişisel bir hevesle geliştirilmiştir.

Basit bir Gezgin Satıcı Problemi (TSP) olarak başlayan bu serüven, zamanla kapasite kısıtlamaları ve çoklu araçları yönetebilen bir Araç Rotalama Problemi (VRP) çözüm aracına dönüştü. Geliştirme sürecinde, bir yol arkadaşı olarak güncel yapay zeka araçlarından da faydalanılmıştır.

## Nasıl Çalıştırılır?

#### 1. Kurulum
```bash
# Projeyi indir ve klasörüne git
git clone https://github.com/fond-of-lapsang-souchong/ACO-TR-LOGISTICS.git
cd ACO-TR-LOGISTICS

# Sanal ortamı kur ve aktif et (macOS/Linux)
python -m venv .venv
source .venv/bin/activate

# Gerekli kütüphaneleri yükle
pip install -r requirements.txt
```

#### 2. Çalıştırma Örnekleri
```bash
# config.yaml'daki varsayılan senaryo ve filo ile çalıştır
python -m src.main

# Akıllı durak seçimi (DBSCAN) stratejisini çalıştır
python -m src.main --strategy dbscan

# Farklı bir senaryo dosyasını çalıştır
python -m src.main --scenario data/scenarios/corlu_merkez_15_durak.json
```
İşlem bitince, sonuç haritası projenin ana dizininde `.html` uzantısıyla oluşturulacaktır. Tüm varsayılan ayarlar (araç filosu, optimizasyon parametreleri vb.) için `config.yaml` dosyasına göz atabilirsin.

#### 3. Testleri Çalıştırma
Projenin temel bileşenlerinin doğru çalıştığını doğrulamak için:
```bash
pytest
```

## Lisans
Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.