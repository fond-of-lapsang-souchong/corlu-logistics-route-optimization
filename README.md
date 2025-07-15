# Proje Adı: ACO-TR-LOGISTICS

Bu proje, Türkiye'deki lojistik operasyonları için **Karınca Kolonisi Optimizasyonu (Ant Colony Optimization - ACO)** algoritmasını kullanarak rota optimizasyonu gerçekleştirmeyi amaçlayan bir Python uygulamasıdır. Projenin temel hedefi, belirli teslimat noktaları arasında seyahat süresini, mesafeyi ve maliyeti en aza indiren en verimli rotaları bulmaktır.

## Projenin Amacı

- **Verimlilik Artışı:** Lojistik ağındaki araçlar için en kısa ve en hızlı rotaları belirleyerek operasyonel verimliliği artırmak.
- **Maliyet Düşürme:** Yakıt tüketimini ve zaman maliyetlerini minimize etmek.
- **Dinamik Rota Planlama:** Gerçek dünya yol ağları üzerinden dinamik ve optimize edilmiş rotalar oluşturmak.
- **Görselleştirme:** Optimize edilen rotaları interaktif haritalar üzerinde görselleştirerek analizi kolaylaştırmak.

## Kullanılacak Teknolojiler

- **Python:** Projenin ana programlama dili.
- **OSMnx:** OpenStreetMap verilerini çekmek, modellemek ve analiz etmek için kullanılan kütüphane. Yol ağlarını ve mesafeleri elde etmek için kullanılacaktır.
- **NumPy:** Hızlı ve verimli sayısal hesaplamalar, özellikle mesafe matrisleri oluşturmak için kullanılacaktır.
- **Folium:** Optimize edilmiş rotaların interaktif Leaflet haritaları üzerinde görselleştirilmesi için kullanılacaktır.
- **VSCodium:** Projenin geliştirileceği özgür ve açık kaynak kodlu IDE.

## Kurulum Adımları

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin.

### 1. Projeyi Klonlama

```bash
git clone <proje_repository_adresi>
cd ACO-TR-LOGISTICS
```

### 2. Sanal Ortam Oluşturma

Proje bağımlılıklarını sisteminizdeki diğer Python paketlerinden izole etmek için bir sanal ortam (virtual environment) oluşturmak en iyi pratiktir.

```bash
python -m venv venv
```

### 3. Sanal Ortamı Aktif Etme

**Windows için:**
```powershell
.\venv\Scripts\Activate.ps1
```
veya
```cmd
.\venv\Scripts\activate
```

**macOS / Linux için:**
```bash
source venv/bin/activate
```

Terminalinizin başında `(venv)` ifadesini gördüğünüzde sanal ortam aktif olmuş demektir.

### 4. Bağımlılıkları Yükleme

Gerekli tüm Python kütüphanelerini `requirements.txt` dosyası üzerinden yükleyin.

```bash
pip install -r requirements.txt
```

## Kullanım

Kurulum tamamlandıktan sonra, projenin ana betiğini çalıştırarak optimizasyon sürecini başlatabilirsiniz.

```bash
python src/main.py
```