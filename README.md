# Proje: ACO-TR-LOGISTICS

Bu proje, Karınca Kolonisi Optimizasyonu (ACO) algoritmasının arkasındaki mantığı anlamak ve gerçek dünya verileriyle denemek için kişisel bir hevesle geliştirilmiştir.

Eğer siz de denemek isterseniz, aşağıdaki adımları izleyebilirsiniz.

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
# Varsayılan senaryoyu (config.yaml'da belirtilen) çalıştır
python -m src.main

# Akıllı durak seçimi (DBSCAN) stratejisini çalıştır
python -m src.main --strategy dbscan

# Farklı bir senaryo dosyasını çalıştır
python -m src.main --scenario data/scenarios/corlu_merkez_15_durak.json

# Rastgele 25 durak ve 100 iterasyonla özel bir deneme yap
python -m src.main --strategy random --num_stops 25 --iterations 100
```
İşlem bitince, sonuç haritası projenin ana dizininde `.html` uzantısıyla oluşturulacaktır. Tüm varsayılan ayarlar için `config.yaml` dosyasına göz atabilirsin.