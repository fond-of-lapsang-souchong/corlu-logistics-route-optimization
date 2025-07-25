import networkx as nx
from tqdm import tqdm
from typing import List, Tuple, Dict

from .ant import Ant
from ..utils import OSRMDistanceProvider 

Graph = nx.MultiDiGraph

class ACOptimizer:
    """
    Manages the ACO process for a Capacitated Vehicle Routing Problem (CVRP)
    with a potentially heterogeneous fleet.
    """
    def __init__(
        self,
        graph: Graph,
        nodes_info: Dict[int, int],
        start_node: int,
        vehicle_fleet: List[int],
        vehicle_fixed_cost: float = 0.0,
        alpha: float = 1.0,
        beta: float = 2.0,
        evaporation_rate: float = 0.5,
    ):
        self.graph = graph
        self.nodes_info = nodes_info
        self.start_node = start_node
        self.vehicle_fleet = vehicle_fleet
        self.vehicle_fixed_cost = vehicle_fixed_cost
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        
        self.distance_cache = OSRMDistanceProvider(self.graph)
        
        self.pheromones = self._init_pheromones()
        
        self.ants = [Ant(self.graph, self.start_node, capacity, self.distance_cache) for capacity in self.vehicle_fleet]
        self.num_ants = len(self.vehicle_fleet)
        self.nodes_to_visit = set(self.nodes_info.keys()) - {self.start_node}

        self.global_best_solution: List[List[List[int]]] = []
        self.global_best_cost: float = float('inf')

    def _init_pheromones(self) -> dict:
        pheromones = {}
        all_nodes = list(self.nodes_info.keys())
        print("Pheromonlar başlatılıyor (mesafe önbelleği kullanılıyor)...")
        for i in range(len(all_nodes)):
            for j in range(i + 1, len(all_nodes)):
                u, v = all_nodes[i], all_nodes[j]
                distance = self.distance_cache.get_distance(u, v)
                initial_pheromone = 1.0 / (distance + 1e-10)
                edge = tuple(sorted((u, v)))
                pheromones[edge] = initial_pheromone
        return pheromones

    def _update_pheromones(self, solutions: List[Tuple[List[List[int]], float]]) -> None:
        for edge in self.pheromones:
            self.pheromones[edge] *= (1 - self.evaporation_rate)
        for tours, cost in solutions:
            if cost == float('inf') or cost == 0:
                continue
            pheromone_deposit = 1.0 / cost
            for tour in tours:
                for i in range(len(tour) - 1):
                    edge = tuple(sorted((tour[i], tour[i+1])))
                    if edge in self.pheromones:
                        self.pheromones[edge] += pheromone_deposit

    def run(self, iterations: int) -> Tuple[List[List[List[int]]], float]:
        progress_bar = tqdm(range(iterations), desc="ACO-VRP Optimizasyonu")
        for i in progress_bar:
            all_solutions = []
            for ant in self.ants:
                ant.reset()
                unvisited_nodes = self.nodes_to_visit.copy()
                while unvisited_nodes:
                    next_node = ant._select_next_node(self.pheromones, {n: self.nodes_info[n] for n in unvisited_nodes}, self.alpha, self.beta)
                    ant.move_to_node(next_node, self.nodes_info)
                    if next_node in unvisited_nodes:
                        unvisited_nodes.remove(next_node)
                ant.finalize_solution()
                num_tours = len([tour for tour in ant.tours if len(tour) > 2]) 
                total_cost = ant.total_distance + (num_tours * self.vehicle_fixed_cost)
                all_solutions.append((ant.tours, total_cost))
                if total_cost < self.global_best_cost:
                    self.global_best_cost = total_cost
                    self.global_best_solution = ant.tours
            
            self._update_pheromones(all_solutions)
            
            progress_bar.set_postfix(
                {
                    "En İyi Maliyet": f"{self.global_best_cost/1000:.2f} km-eşdeğeri",
                    "İterasyon": f"{i + 1}/{iterations}"
                }
            )
        
        self.distance_cache.save_to_disk()
        return self.global_best_solution, self.global_best_cost