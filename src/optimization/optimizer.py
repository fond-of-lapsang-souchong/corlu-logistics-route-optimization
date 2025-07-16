import networkx as nx
from tqdm import tqdm
from typing import List, Tuple, Set

from .ant import Ant
from ..utils import DistanceCache

Graph = nx.MultiDiGraph

class ACOptimizer:
    """
    Manages the entire Ant Colony Optimization process, using a DistanceCache
    for performance optimization.
    """
    def __init__(
        self,
        graph: Graph,
        nodes_to_visit: List[int],
        start_node: int,
        ant_count: int,
        alpha: float = 1.0,
        beta: float = 5.0,
        evaporation_rate: float = 0.5,
    ):
        self.graph = graph
        self.nodes_to_visit: Set[int] = set(nodes_to_visit)
        self.start_node = start_node
        self.ant_count = ant_count
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        
        self.distance_cache = DistanceCache(self.graph)

        self.pheromones = self._init_pheromones()
        
        self.ants = [Ant(self.graph, self.start_node, self.distance_cache) for _ in range(self.ant_count)]

        self.global_best_path: List[int] = []
        self.global_best_distance: float = float('inf')

    def _init_pheromones(self) -> dict:
        """
        Initializes pheromones based on distances from the cache.
        """
        pheromones = {}
        all_nodes = list(self.nodes_to_visit)
        print("Pheromonlar başlatılıyor (mesafe önbelleği kullanılıyor)...")
        for i in range(len(all_nodes)):
            for j in range(i + 1, len(all_nodes)):
                u, v = all_nodes[i], all_nodes[j]
                distance = self.distance_cache.get_distance(u, v)
                
                if distance == float('inf'):
                    initial_pheromone = 0.01
                else:
                    initial_pheromone = 1.0
                
                edge = tuple(sorted((u, v)))
                pheromones[edge] = initial_pheromone
        return pheromones

    def _update_pheromones(self, all_tours: List[Tuple[List[int], float]]) -> None:
        """Updates the pheromone matrix after each iteration."""
        for edge in self.pheromones:
            self.pheromones[edge] *= (1 - self.evaporation_rate)

        for path, distance in all_tours:
            if distance == float('inf') or distance == 0:
                continue
            
            pheromone_deposit = 1.0 / distance
            
            for i in range(len(path) - 1):
                edge = tuple(sorted((path[i], path[i+1])))
                if edge in self.pheromones:
                    self.pheromones[edge] += pheromone_deposit

    def run(self, iterations: int) -> Tuple[List[int], float]:
        """Runs the main ACO optimization loop."""
        
        progress_bar = tqdm(range(iterations), desc="ACO Optimizasyonu")

        for i in progress_bar:
            all_tours = []
            for ant in self.ants:
                ant.reset()
                
                while len(ant.visited) < len(self.nodes_to_visit):
                    next_node = ant._select_next_node(
                        self.pheromones, self.nodes_to_visit, self.alpha, self.beta
                    )
                    ant._update_path(next_node)
                
                ant._update_path(ant.start_node)

                tour_distance = ant.path_distance
                all_tours.append((ant.path, tour_distance))

                if tour_distance < self.global_best_distance:
                    self.global_best_distance = tour_distance
                    self.global_best_path = ant.path
            
            self._update_pheromones(all_tours)
            
            progress_bar.set_postfix(
                {
                    "En İyi Mesafe": f"{self.global_best_distance/1000:.2f} km",
                    "İterasyon": f"{i + 1}/{iterations}"
                }
            )
        
        progress_bar.close()

        self.distance_cache.save_to_disk()

        return self.global_best_path, self.global_best_distance