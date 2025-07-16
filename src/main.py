import os
import sys
import yaml
import random
import time

from src.data_loader import load_graph
from src.optimization import ACOptimizer
from src.visualization.map_plotter import plot_optimized_route

def load_config(config_path: str = 'config.yaml') -> dict:
    """
    Loads the YAML configuration file.
    """
    print(f"'{config_path}' adresinden yapılandırma yükleniyor...")
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print("Yapılandırma başarıyla yüklendi.")
        return config
    except FileNotFoundError:
        print(f"HATA: '{config_path}' bulunamadı. Lütfen bir yapılandırma dosyası oluşturun.")
        sys.exit(1) 
    except yaml.YAMLError as e:
        print(f"HATA: Yapılandırma dosyası okunurken bir hata oluştu: {e}")
        sys.exit(1)

def main():
    """
    The main function to run the entire ACO logistics optimization process.
    """
    config = load_config()
    
    place_name = config['location']['place_name']
    print(f"\n'{place_name}' için yol ağı indiriliyor...")
    G_directed = load_graph(place_name, undirected=False, verbose=False) 
    G_undirected = G_directed.to_undirected()
    print("Yol ağı başarıyla indirildi ve hazırlandı.")

    num_stops = config['problem']['num_stops']
    all_nodes = list(G_undirected.nodes())
    if len(all_nodes) < num_stops:
        print(f"HATA: Graf yeterli sayıda düğüm içermiyor ({len(all_nodes)} < {num_stops}).")
        sys.exit(1)
        
    nodes_to_visit = random.sample(all_nodes, num_stops)
    start_node = nodes_to_visit[0]
    print(f"Optimizasyon için {num_stops} adet rastgele durak seçildi.")

    print("\nOptimizasyon süreci başlıyor...")
    start_time = time.time()

    aco_params = config['aco']
    optimizer = ACOptimizer(
        graph=G_undirected,
        nodes_to_visit=nodes_to_visit,
        start_node=start_node,
        ant_count=aco_params['ant_count'],
        alpha=aco_params['alpha'],
        beta=aco_params['beta'],
        evaporation_rate=aco_params['evaporation_rate']
    )
    
    best_path, best_distance = optimizer.run(aco_params['iterations'])
    
    end_time = time.time()
    print(f"\nOptimizasyon tamamlandı! Toplam süre: {end_time - start_time:.2f} saniye")

    if best_path:
        print("\n--- SONUÇLAR ---")
        print(f"En iyi bulunan tur mesafesi: {best_distance / 1000:.2f} km")
        
        print("Sonuç haritası oluşturuluyor...")
        route_map = plot_optimized_route(
            graph=G_directed,
            best_path=best_path,
            nodes_to_visit=nodes_to_visit,
            start_node=start_node
        )
        
        if route_map:
            output_filename = config['output']['map_filename']
            route_map.save(output_filename)
            print(f"Harita başarıyla '{os.path.abspath(output_filename)}' adresine kaydedildi.")
        else:
            print("Harita oluşturulamadı.")
    else:
        print("Optimizasyon bir sonuç üretemedi.")


if __name__ == "__main__":
    main()