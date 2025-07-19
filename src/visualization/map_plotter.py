import folium
import osmnx as ox
import networkx as nx
import pandas as pd
import numpy as np
from folium.plugins import MarkerCluster, BeautifyIcon
from typing import List, Optional

def plot_optimized_route(
    graph: nx.MultiDiGraph,
    best_path: List[int],
    nodes_to_visit: List[int],
    start_node: int
) -> Optional[folium.Map]:
    """
    Optimize edilmiş rotayı, sıralı durakları ve "gökkuşağı" rotasıyla
    interaktif bir Folium haritası üzerinde çizer.
    """
    if not best_path or not graph:
        print("Çizilecek bir rota veya graf bulunamadı.")
        return None

    print("Ara yollar hesaplanıyor ve harita geometrileri oluşturuluyor...")
    
    num_segments = len(best_path) - 1
    colors = ox.plot.get_colors(num_segments, cmap='plasma', start=0.1, stop=0.9)
    
    list_of_route_gdfs = []

    for i in range(num_segments):
        source = best_path[i]
        target = best_path[i+1]
        
        try:
            path_segment_nodes = ox.shortest_path(graph, source, target, weight='length')
            
            if path_segment_nodes and len(path_segment_nodes) > 1:
                segment_gdf = ox.routing.route_to_gdf(graph, path_segment_nodes, weight="length")
                segment_gdf['color'] = colors[i]
                list_of_route_gdfs.append(segment_gdf)
                
        except nx.NetworkXNoPath:
            print(f"UYARI: {source} -> {target} arasında yönlü yol bulunamadı. Bu segment haritada gösterilmeyecek.")
            continue

    if not list_of_route_gdfs:
        print("HATA: Çizilecek kadar geçerli bir yol segmenti bulunamadı.")
        return None
    
    route_gdf = pd.concat(list_of_route_gdfs)
    
    route_map = folium.Map(tiles="CartoDB positron")
    folium.GeoJson(
        route_gdf,
        style_function=lambda feature: {
            "color": feature['properties']['color'],
            "weight": 6,
            "opacity": 0.8,
        }
    ).add_to(route_map)
    
    route_map.fit_bounds(folium.GeoJson(route_gdf).get_bounds())

    marker_cluster = MarkerCluster().add_to(route_map)

    start_lat = graph.nodes[start_node]['y']
    start_lon = graph.nodes[start_node]['x']
    folium.Marker(
        location=(start_lat, start_lon),
        icon=folium.Icon(color='darkgreen', icon='truck', prefix='fa'),
        popup=f'<b>DEPO (Başlangİç/Bitiş)</b><br>ID: {start_node}'
    ).add_to(route_map)
    
    for i, node_id in enumerate(best_path):
        if i > 0 and i < len(best_path) - 1:
            stop_lat = graph.nodes[node_id]['y']
            stop_lon = graph.nodes[node_id]['x']
            
            folium.Marker(
                location=(stop_lat, stop_lon),
                icon=BeautifyIcon(
                    number=i,
                    icon_shape='marker',
                    border_color='darkred',
                    background_color='#FFC0CB',
                    text_color='darkred'
                ),
                popup=f'<b>{i}. Durak</b><br>ID: {node_id}'
            ).add_to(marker_cluster)

    return route_map