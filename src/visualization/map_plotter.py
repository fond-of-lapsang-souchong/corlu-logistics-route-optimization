import folium
import osmnx as ox
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from folium.plugins import MarkerCluster
from typing import List, Optional, Dict

def plot_optimized_route(
    graph: nx.MultiDiGraph,
    best_solution: List[List[int]],
    nodes_to_visit: List[int],
    start_node: int,
    nodes_info: Dict[int, int] 
) -> Optional[folium.Map]:
    """
    Kapasiteli Araç Rotalama Problemi (VRP) çözümünü, her araç için
    farklı renklerdeki rotalarla interaktif bir harita üzerinde çizer.
    """
    if not best_solution:
        print("Çizilecek bir çözüm bulunamadı.")
        return None

    print("Araç turları için ara yollar hesaplanıyor ve harita geometrileri oluşturuluyor...")
    
    cmap_list = ['plasma', 'viridis', 'cividis', 'inferno', 'magma', 'coolwarm']
    
    all_routes_gdf = []

    for vehicle_index, tour in enumerate(best_solution):
        num_segments = len(tour) - 1
        if num_segments <= 0:
            continue
            
        cmap = cmap_list[vehicle_index % len(cmap_list)]
        colors = ox.plot.get_colors(num_segments, cmap=cmap, start=0.1, stop=0.9)

        for i in range(num_segments):
            source = tour[i]
            target = tour[i+1]
            try:
                path_segment_nodes = ox.shortest_path(graph, source, target, weight='length')
                if path_segment_nodes and len(path_segment_nodes) > 1:
                    segment_gdf = ox.routing.route_to_gdf(graph, path_segment_nodes, weight="length")
                    segment_gdf['color'] = colors[i]
                    segment_gdf['vehicle'] = vehicle_index + 1
                    all_routes_gdf.append(segment_gdf)
            except nx.NetworkXNoPath:
                print(f"UYARI: {source} -> {target} arasında yönlü yol bulunamadı. Bu segment haritada gösterilmeyecek.")
                continue

    if not all_routes_gdf:
        print("HATA: Çizilecek kadar geçerli bir yol segmenti bulunamadı.")
        return None
    
    route_gdf = pd.concat(all_routes_gdf)
    
    route_map = folium.Map(tiles="CartoDB positron")
    
    folium.GeoJson(
        route_gdf,
        style_function=lambda feature: {
            "color": feature['properties']['color'],
            "weight": 5,
            "opacity": 0.8,
        }
    ).add_to(route_map)
    
    route_map.fit_bounds(folium.GeoJson(route_gdf).get_bounds())

    marker_cluster = MarkerCluster().add_to(route_map)
    
    folium.Marker(
        location=(graph.nodes[start_node]['y'], graph.nodes[start_node]['x']),
        icon=folium.Icon(color='darkgreen', icon='truck', prefix='fa'),
        popup=f'<b>DEPO</b><br>ID: {start_node}'
    ).add_to(route_map)
    
    visited_stops = set(nodes_to_visit) - {start_node}
    for node_id in visited_stops:
        demand = nodes_info.get(node_id, "Bilinmiyor")
        folium.Marker(
            location=(graph.nodes[node_id]['y'], graph.nodes[node_id]['x']),
            icon=folium.Icon(color='darkred', icon='info-sign'),
            popup=f'<b>Durak ID: {node_id}</b><br>Talep: {demand}'
        ).add_to(marker_cluster)

    return route_map

def plot_convergence(history: list, filename: str):
    """
    Plots the convergence of the algorithm over iterations and saves it to a file.
    """
    if not history or all(cost == float('inf') for cost in history):
        print("UYARI: Geçerli maliyet geçmişi bulunamadı, yakınsama grafiği oluşturulamıyor.")
        return

    print("Yakınsama grafiği oluşturuluyor...")
    plt.figure(figsize=(12, 6))
    
    history_km = [cost / 1000 if cost != float('inf') else float('nan') for cost in history]
    
    plt.plot(history_km, marker='o', linestyle='-', color='b', markersize=4)
    plt.title('Optimizasyonun İterasyonlara Göre Yakınsaması')
    plt.xlabel('İterasyon')
    plt.ylabel('En İyi Maliyet (km-eşdeğeri)')
    plt.grid(True)
    
    valid_costs = [cost for cost in history_km if cost is not None and not (isinstance(cost, float) and cost != cost)]
    if valid_costs:
        min_cost = min(valid_costs)
        min_iter = history_km.index(min_cost)
        plt.axhline(y=min_cost, color='r', linestyle='--', label=f'En İyi: {min_cost:.2f} km')
        plt.plot(min_iter, min_cost, 'r*', markersize=15)

    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    print(f"Yakınsama grafiği başarıyla '{filename}' adresine kaydedildi.")
    plt.close()