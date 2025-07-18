# Proje: ACO-TR-LOGISTICS

Bu proje, Karınca Kolonisi Optimizasyonu (ACO) algoritmasının arkasındaki mantığı anlamak ve gerçek dünya verileriyle denemek için kişisel bir hevesle geliştirilmiştir.

Eğer siz de denemek isterseniz, aşağıdaki adımları izleyebilirsiniz.

## Nasıl Çalıştırılır?

#### 1. Projeyi Bilgisayarınıza İndirin
```bash
git clone https://github.com/fond-of-lapsang-souchong/ACO-TR-LOGISTICS.git
cd ACO-TR-LOGISTICS
```

#### 2. Sanal Ortamı Kurun ve Aktif Edin
Bu, proje için gerekli kütüphanelerin bilgisayarınızdaki diğer projelere karışmasını engeller.
```bash
# Sanal ortamı oluşturun
python -m venv .venv

# Aktif hale getirin (macOS / Linux için)
source .venv/bin/activate
```

#### 3. Gerekli Kütüphaneleri Yükleyin
```bash
pip install -r requirements.txt
```

#### 4. Optimizasyonu Başlatın
Aşağıdaki komut, `config.yaml` dosyasındaki ayarlara göre optimizasyonu çalıştıracaktır.
```bash
python -m src.main
```

İşlem tamamlandığında, projenin ana klasöründe **`corlu_optimized_route.html`** adında interaktif bir harita dosyası oluşturulacaktır. Bu dosyayı web tarayıcınızda açarak sonucu görebilirsiniz.

## Ayarlar
Farklı bir şehir denemek veya karınca sayısı gibi parametreleri değiştirmek isterseniz, **`config.yaml`** dosyasını düzenleyebilirsiniz.