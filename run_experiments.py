import csv
import time
import numpy as np
from copy import deepcopy
from src.data_loader import load_graph 
from src.main import load_config, run_optimization_instance

def run_experiments():
    """
    Grafiği sadece bir kez yükleyerek, farklı parametre kombinasyonlarını
    sistematik olarak test eder ve sonuçları bir CSV dosyasına kaydeder.
    """
    base_config = load_config()
    
    place_name = base_config['location']['place_name']
    print(f"\nAna Deney için '{place_name}' yol ağı yükleniyor...")
    G_directed = load_graph(place_name, undirected=False, verbose=True)
    if G_directed is None:
        print("Graf yüklenemedi, deneyler iptal edildi.")
        return
    G_undirected = G_directed.to_undirected()
    print("Yol ağı deneye hazır.")

    parameter_grid = [
        {'strategy': 'eas', 'elitism_factor': 1.0},
        {'strategy': 'eas', 'elitism_factor': 5.0},
        {'strategy': 'eas', 'elitism_factor': 10.0},
        {'strategy': 'mmas', 'rho': 0.1},
        {'strategy': 'mmas', 'rho': 0.2},
        {'strategy': 'mmas', 'rho': 0.5},
    ]

    num_runs_per_setting = 5

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    results_filename = f"experiment_results_{timestamp}.csv"
    
    with open(results_filename, 'w', newline='') as csvfile:
        fieldnames = ['strategy', 'elitism_factor', 'rho', 'run', 'best_cost_km', 'time_seconds']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for params in parameter_grid:
            print(f"\n--- Yeni Deney Başlıyor: {params} ---")
            
            costs = []
            times = []

            for i in range(num_runs_per_setting):
                print(f"  -> Çalıştırma {i+1}/{num_runs_per_setting}...")
                
                current_config = deepcopy(base_config)
                
                current_config['aco']['strategy'] = params['strategy']
                if params['strategy'] == 'eas':
                    current_config['aco']['elitism_factor'] = params['elitism_factor']
                elif params['strategy'] == 'mmas':
                    current_config['aco']['mmas']['rho'] = params['rho']
                
                results = run_optimization_instance(
                    current_config, 
                    G_directed, 
                    G_undirected
                )

                if results is None:
                    print("  -> Bu çalıştırma başarısız oldu, atlanıyor.")
                    continue

                best_solution, best_cost, cost_history, elapsed_time, nodes_info_used, start_node_used = results

                if best_cost is not None and best_cost != float('inf'):
                    costs.append(best_cost / 1000)
                    times.append(elapsed_time)
                    
                    row = {
                        'strategy': params.get('strategy', 'N/A'),
                        'elitism_factor': params.get('elitism_factor', 'N/A'),
                        'rho': params.get('rho', 'N/A'),
                        'run': i + 1,
                        'best_cost_km': best_cost / 1000,
                        'time_seconds': elapsed_time
                    }
                    writer.writerow(row)

            if costs:
                avg_cost = np.mean(costs)
                std_cost = np.std(costs)
                print(f"  -> ÖZET: Ortalama Maliyet = {avg_cost:.2f} km, Std. Sapma = {std_cost:.2f} km")

    print(f"\nTüm deneyler tamamlandı. Sonuçlar '{results_filename}' dosyasına kaydedildi.")

if __name__ == "__main__":
    run_experiments()