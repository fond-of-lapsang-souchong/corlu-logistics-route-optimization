import os
import json
import networkx as nx
from typing import Dict, Tuple

Graph = nx.MultiDiGraph
CacheDict = Dict[Tuple[int, int], float]

class DistanceCache:
    """
    Manages a two-level cache for node-to-node distances to speed up
    repeated shortest_path calculations.

    Level 1: In-memory dictionary for the current session (fastest).
    Level 2: A JSON file for persistence across different runs (slower but permanent).
    """

    def __init__(self, graph: Graph, cache_filepath: str = "data/cache/distance_cache.json"):
        """
        Initializes the DistanceCache.

        Args:
            graph (Graph): The OSMnx graph used for path calculations.
            cache_filepath (str): The path to the persistent JSON cache file.
        """
        print("Mesafe önbelleği (DistanceCache) başlatılıyor...")
        self.graph = graph
        self.cache_filepath = cache_filepath
        
        self.memory_cache: CacheDict = {}

        self.load_from_disk()

    def get_distance(self, u: int, v: int) -> float:
        """
        Gets the shortest path distance between two nodes, using the cache if possible.

        Args:
            u (int): The starting node.
            v (int): The ending node.

        Returns:
            float: The shortest path distance in meters, or float('inf') if no path exists.
        """
        if u == v:
            return 0.0

        edge = tuple(sorted((u, v)))

        if edge in self.memory_cache:
            return self.memory_cache[edge]

        try:
            distance = nx.shortest_path_length(self.graph, u, v, weight='length')
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            distance = float('inf')
        
        self.memory_cache[edge] = distance
        
        return distance

    def load_from_disk(self) -> None:
        """
        Loads the persistent cache from the JSON file into the in-memory cache.
        """
        if os.path.exists(self.cache_filepath) and os.path.getsize(self.cache_filepath) > 0:
            print(f"'{self.cache_filepath}' adresinden kalıcı önbellek yükleniyor...")
            try:
                with open(self.cache_filepath, 'r') as f:
                    str_key_cache: Dict[str, float] = json.load(f)
                    self.memory_cache = {eval(key): value for key, value in str_key_cache.items()}
                print(f"{len(self.memory_cache)} adet mesafe önbellekten yüklendi.")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Önbellek dosyası okunurken hata oluştu: {e}. Boş bir önbellek ile devam ediliyor.")
                self.memory_cache = {}
        else:
            print("Kalıcı önbellek dosyası bulunamadı veya boş. Yeni bir önbellek oluşturulacak.")
            self.memory_cache = {}

    def save_to_disk(self) -> None:
        """
        Saves the in-memory cache to the persistent JSON file.
        This should be called at the end of the program.
        """
        print(f"Güncel mesafe önbelleği '{self.cache_filepath}' adresine kaydediliyor...")
        
        str_key_cache = {str(key): value for key, value in self.memory_cache.items()}

        os.makedirs(os.path.dirname(self.cache_filepath), exist_ok=True)
        
        with open(self.cache_filepath, 'w') as f:
            json.dump(str_key_cache, f, indent=4)
        
        print(f"{len(str_key_cache)} adet mesafe başarıyla kalıcı önbelleğe kaydedildi.")
    
def update_config_with_args(config: dict, args) -> dict:
    """
    Updates the configuration dictionary with arguments passed from the command line.

    Args:
        config (dict): The base configuration loaded from the YAML file.
        args: The arguments object parsed by argparse.

    Returns:
        dict: The updated configuration dictionary.
    """
    arg_to_config_map = {
        'strategy': ('problem', 'strategy'),
        'num_stops': ('problem', 'num_stops'),
        'scenario': ('problem', 'scenario_filepath'),
        'ants': ('aco', 'ant_count'),
        'iterations': ('aco', 'iterations'),
        'output': ('output', 'map_filename'),
    }

    for arg_name, config_keys in arg_to_config_map.items():
        arg_value = getattr(args, arg_name, None)
        
        if arg_value is not None:
            temp_dict = config
            for key in config_keys[:-1]:
                temp_dict = temp_dict[key]
            temp_dict[config_keys[-1]] = arg_value
            print(f"Yapılandırma güncellendi: '{'.'.join(config_keys)}' -> {arg_value}")

    return config