import folium
import osmnx as ox
import networkx as nx
from typing import List, Optional

def plot_optimized_route(
    graph: nx.MultiDiGraph,
    best_path: List[int],
    nodes_to_visit: List[int],
    start_node: int
) -> Optional[folium.Map]:
    if not best_path or not graph:
        print("Çizilecek bir rota veya graf bulunamadı.")
        return None

    try:
        full_detailed_route = []
        for i in range(len(best_path) - 1):
            source = best_path[i]
            target = best_path[i+1]
            
            path_segment = ox.shortest_path(graph, source, target, weight='length')
            
            if path_segment:
                full_detailed_route.extend(path_segment[:-1])
        
        if best_path:
            full_detailed_route.append(best_path[-1])
            
        if not full_detailed_route:
            print("Duraklar arasında tam bir rota hesaplanamadı.")
            return None

        route_gdf = ox.routing.route_to_gdf(graph, full_detailed_route, weight="length")

        route_center_y = route_gdf.unary_union.centroid.y
        route_center_x = route_gdf.unary_union.centroid.x
        route_map = folium.Map(location=[route_center_y, route_center_x], zoom_start=13, tiles="OpenStreetMap")

        folium.GeoJson(
            route_gdf,
            style_function=lambda x: {"color": "blue", "weight": 5, "opacity": 0.7}
        ).add_to(route_map)

        start_lat = graph.nodes[start_node]['y']
        start_lon = graph.nodes[start_node]['x']
        folium.Marker(
            location=(start_lat, start_lon),
            icon=folium.Icon(color='green', icon='play'),
            popup='Başlangıç/Bitiş'
        ).add_to(route_map)

        for node in nodes_to_visit:
            if node != start_node and node in graph.nodes:
                stop_lat = graph.nodes[node]['y']
                stop_lon = graph.nodes[node]['x']
                folium.Marker(
                    location=(stop_lat, stop_lon),
                    icon=folium.Icon(color='red', icon='info-sign'),
                    popup=f'Durak: {node}'
                ).add_to(route_map)

        return route_map

    except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
        print(f"Harita çizimi için rota hesaplanırken bir hata oluştu: İki durak arasında yol bulunamadı. {e}")
        return None
    except Exception as e:
        print(f"Harita çizimi sırasında beklenmedik bir hata oluştu: {e}")
        return None