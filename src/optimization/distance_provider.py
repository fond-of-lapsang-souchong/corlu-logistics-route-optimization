import requests
import networkx as nx
from typing import Dict, Tuple

class OSRMDistanceProvider:
    """
    Calculates distances by querying a local OSRM server.
    It keeps an in-memory cache to avoid repeated API calls for the same pair.
    """
    def __init__(self, graph: nx.Graph, host: str = 'http://127.0.0.1:5000'):
        self.host = host
        self.node_coords = self._extract_node_coords(graph)
        self._cache: Dict[Tuple[int, int], float] = {}
        print(f"OSRM Mesafe Sağlayıcı başlatıldı. Sunucu: {self.host}")

    def _extract_node_coords(self, graph: nx.Graph) -> Dict[int, Tuple[float, float]]:
        """Extracts longitude and latitude for each node from the graph."""
        coords = {}
        for node, data in graph.nodes(data=True):
            coords[node] = (data['x'], data['y'])
        return coords

    def get_distance(self, u_node: int, v_node: int) -> float:
        """
        Gets the driving distance in meters between two nodes.
        First checks the local cache, then queries the OSRM server if not found.
        """
        if u_node == v_node:
            return 0.0

        edge = tuple(sorted((u_node, v_node)))
        if edge in self._cache:
            return self._cache[edge]

        try:
            lon1, lat1 = self.node_coords[u_node]
            lon2, lat2 = self.node_coords[v_node]
        except KeyError as e:
            print(f"HATA: Düğüm ID'si {e} için koordinat bulunamadı.")
            return float('inf')

        url = f"{self.host}/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"

        try:
            response = requests.get(url, timeout=10) 
            response.raise_for_status() 
            data = response.json()
            
            if data['code'] == 'Ok' and data.get('routes'):
                distance_meters = data['routes'][0]['distance']
                self._cache[edge] = distance_meters 
                return distance_meters
            else:
                print(f"UYARI: OSRM {u_node} ve {v_node} arasında rota bulamadı. Cevap: {data.get('code')}")
                self._cache[edge] = float('inf')
                return float('inf')

        except requests.exceptions.RequestException as e:
            print(f"KRİTİK HATA: OSRM sunucusuna bağlanılamadı ({self.host}). Lütfen Docker container'ının çalıştığından emin olun. Hata: {e}")
            return float('inf')

    def save_to_disk(self):
        print("OSRM önbelleği oturum belleğinde tutuldu, diske otomatik kaydedilmedi.")