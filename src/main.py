import os
import sys
import yaml
import random
import time
import json
import argparse
import numpy as np
from sklearn.cluster import DBSCAN

from src.data_loader import load_graph
from src.optimization import ACOptimizer
from src.visualization.map_plotter import plot_optimized_route
from src.utils import update_config_with_args

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

def parse_arguments():
    """
    Parses command-line arguments to override config file settings.
    """
    parser = argparse.ArgumentParser(description="ACO-TR-LOGISTICS: Rota Optimizasyon Uygulaması")
    
    parser.add_argument('--strategy', type=str, help="Durak seçme stratejisi: 'random', 'from_scenario', veya 'dbscan'.")
    parser.add_argument('--num_stops', type=int, help="'random' stratejisi için durak sayısı.")
    parser.add_argument('--scenario', type=str, help="'from_scenario' stratejisi için senaryo dosyasının yolu.")
    
    parser.add_argument('--iterations', type=int, help="Optimizasyon iterasyon sayısı.")
    parser.add_argument('--output', type=str, help="Sonuç haritasının kaydedileceği dosya adı.")

    return parser.parse_args()


def main():
    """
    The main function to run the entire ACO logistics optimization process.
    """
    args = parse_arguments()
    config = load_config()
    config = update_config_with_args(config, args)
    
    place_name = config['location']['place_name']
    print(f"\n'{place_name}' için yol ağı indiriliyor...")
    G_directed = load_graph(place_name, undirected=False, verbose=False)
    G_undirected = G_directed.to_undirected()
    print("Yol ağı başarıyla indirildi ve hazırlandı.")

    print("\nProblem tanımlanıyor (duraklar ve talepler seçiliyor)...")
    problem_config = config['problem']
    strategy = problem_config.get('strategy', 'random')

    nodes_info: dict[int, int] = {}
    
    if strategy == "from_scenario":
        scenario_path = problem_config.get('scenario_filepath')
        if not scenario_path:
            print("HATA: Strateji 'from_scenario' olarak ayarlanmış ancak 'scenario_filepath' belirtilmemiş.")
            sys.exit(1)
        
        try:
            with open(scenario_path, 'r') as f:
                scenario = json.load(f)
                nodes_info = {int(node_id): int(demand) for node_id, demand in scenario['nodes']}
            print(f"'{scenario_path}' senaryosundan {len(nodes_info)} adet durak/talep yüklendi.")
        except Exception as e:
            print(f"HATA: Senaryo dosyası '{scenario_path}' okunurken hata oluştu: {e}")
            sys.exit(1)
            
    elif strategy == "random":
        random_params = problem_config.get('random_stops', {})
        num_stops = random_params.get('num_stops', 10)
        min_demand = random_params.get('min_demand', 1)
        max_demand = random_params.get('max_demand', 10)
        
        all_nodes = list(G_undirected.nodes())
        if len(all_nodes) < num_stops:
            print(f"HATA: Graf yeterli sayıda düğüm içermiyor ({len(all_nodes)} < {num_stops}).")
            sys.exit(1)
        
        selected_nodes = random.sample(all_nodes, num_stops)
        nodes_info = {node_id: random.randint(min_demand, max_demand) for node_id in selected_nodes}
        print(f"Optimizasyon için {num_stops} adet rastgele durak ve talep oluşturuldu.")

    elif strategy == "dbscan":
        dbscan_params = problem_config.get('dbscan', {})
        random_params = problem_config.get('random_stops', {})
        eps = dbscan_params.get('eps', 0.01)
        min_samples = dbscan_params.get('min_samples', 5)
        min_demand = random_params.get('min_demand', 1)
        max_demand = random_params.get('max_demand', 10)

        nodes_data = G_undirected.nodes(data=True)
        coords = np.array([[data['x'], data['y']] for _, data in nodes_data])
        node_ids = np.array([node_id for node_id, _ in nodes_data])

        db = DBSCAN(eps=eps, min_samples=min_samples).fit(coords)
        labels = db.labels_
        unique_labels = set(labels)
        if -1 in unique_labels: unique_labels.remove(-1)
        selected_nodes = []

        if not unique_labels:
             print("HATA: DBSCAN hiçbir küme bulamadı. Lütfen 'eps' veya 'min_samples' parametrelerini değiştirmeyi deneyin.")
             sys.exit(1)
            
        
        for label in unique_labels:
            cluster_indices = np.where(labels == label)[0]
            random_index = random.choice(cluster_indices)
            selected_nodes.append(int(node_ids[random_index]))
        
        nodes_info = {node_id: random.randint(min_demand, max_demand) for node_id in selected_nodes}
        print(f"DBSCAN ile {len(nodes_info)} küme/durak bulundu ve rastgele talepler atandı.")
    
    else:
        print(f"HATA: Geçersiz problem stratejisi: '{strategy}'.")
        sys.exit(1)

    if not nodes_info:
        print("HATA: Ziyaret edilecek hiçbir durak bulunamadı.")
        sys.exit(1)
        
    start_node = list(nodes_info.keys())[0]
    nodes_info[start_node] = 0 
    
    print("\nOptimizasyon süreci başlıyor...")
    start_time = time.time()

    aco_params = config['aco']
    optimizer = ACOptimizer(
        graph=G_undirected,
        nodes_info=nodes_info,
        start_node=start_node,
        vehicle_fleet=aco_params['vehicle_fleet'],
        vehicle_fixed_cost=aco_params.get('vehicle_fixed_cost', 0.0),
        alpha=aco_params['alpha'],
        beta=aco_params['beta'],
        evaporation_rate=aco_params['evaporation_rate']
    )
    
    best_solution, best_cost = optimizer.run(aco_params['iterations'])
    
    end_time = time.time()
    print(f"\nOptimizasyon tamamlandı! Toplam süre: {end_time - start_time:.2f} saniye")

    if best_solution:
        print("\n--- SONUÇLAR ---")
        print(f"En iyi bulunan çözümün toplam maliyeti: {best_cost / 1000:.2f} km-eşdeğeri")
        print(f"Toplam {len(best_solution)} araç turu (rota) bulundu.")
        
        print("Sonuç haritası oluşturuluyor...")
        nodes_to_visit = list(nodes_info.keys())
        route_map = plot_optimized_route(
            graph=G_directed,
            best_solution=best_solution,
            nodes_to_visit=nodes_to_visit,
            start_node=start_node,
            nodes_info=nodes_info
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