import networkx as nx
from tqdm import tqdm
from typing import List, Tuple, Dict

from .ant import Ant
from ..utils import OSRMDistanceProvider

Graph = nx.MultiDiGraph

class ACOptimizer:
    def __init__(
        self,
        graph: Graph,
        nodes_info: Dict[int, int],
        start_node: int,
        vehicle_fleet: List[int],
        osrm_host: str,
        aco_strategy: str = "eas",
        vehicle_fixed_cost: float = 0.0,
        alpha: float = 1.0,
        beta: float = 2.0,
        evaporation_rate: float = 0.5,
        eas_elitism_factor: float = 1.0,
        mmas_rho: float = 0.2
    ):
        self.graph = graph
        self.nodes_info = nodes_info
        self.start_node = start_node
        self.vehicle_fleet = vehicle_fleet
        self.osrm_host = osrm_host
        self.vehicle_fixed_cost = vehicle_fixed_cost
        
        self.strategy = aco_strategy
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        
        self.eas_elitism_factor = eas_elitism_factor
        self.mmas_rho = mmas_rho
        
        self.pheromone_min = 0.0
        self.pheromone_max = float('inf')
        self.mmas_initialized = False

        self.distance_cache = OSRMDistanceProvider(self.graph, host=self.osrm_host)
        self.pheromones = self._init_pheromones()
        
        self.ants = [Ant(self.graph, self.start_node, capacity, self.distance_cache) for capacity in self.vehicle_fleet]
        self.num_ants = len(self.vehicle_fleet)
        self.nodes_to_visit = set(self.nodes_info.keys()) - {self.start_node}

        self.global_best_solution: List[List[int]] = []
        self.global_best_cost: float = float('inf')

    def _init_pheromones(self) -> dict:
        pheromones = {}
        all_nodes = list(self.nodes_info.keys())
        print("Pheromonlar ön-başlatılıyor...")
        for i in range(len(all_nodes)):
            for j in range(i + 1, len(all_nodes)):
                edge = tuple(sorted((all_nodes[i], all_nodes[j])))
                pheromones[edge] = 1.0
        return pheromones
    
    def _update_pheromones_eas(self, solutions: List[Tuple[List[List[int]], float]]):
        for edge in self.pheromones:
            self.pheromones[edge] *= (1 - self.evaporation_rate)

        for tours, cost in solutions:
            if cost == float('inf') or cost == 0: continue
            pheromone_deposit = 1.0 / cost
            for tour in tours:
                for i in range(len(tour) - 1):
                    edge = tuple(sorted((tour[i], tour[i+1])))
                    if edge in self.pheromones:
                        self.pheromones[edge] += pheromone_deposit

        if self.global_best_cost != float('inf'):
            elitist_deposit = self.eas_elitism_factor * (1.0 / self.global_best_cost)
            for tour in self.global_best_solution:
                for i in range(len(tour) - 1):
                    edge = tuple(sorted((tour[i], tour[i+1])))
                    if edge in self.pheromones:
                        self.pheromones[edge] += elitist_deposit

    def _update_pheromones_mmas(self, best_solution_of_iteration: Tuple[List[List[int]], float]):
        for edge in self.pheromones:
            self.pheromones[edge] *= (1 - self.mmas_rho)

        tours, cost = best_solution_of_iteration
        if cost != float('inf'):
            pheromone_deposit = 1.0 / cost
            for tour in tours:
                for i in range(len(tour) - 1):
                    edge = tuple(sorted((tour[i], tour[i+1])))
                    if edge in self.pheromones:
                        self.pheromones[edge] += pheromone_deposit
        
        for edge in self.pheromones:
            self.pheromones[edge] = max(self.pheromone_min, min(self.pheromones[edge], self.pheromone_max))

    def run(self, iterations: int) -> Tuple[List[List[int]], float, List[float]]:
        cost_history = []
        progress_bar = tqdm(range(iterations), desc=f"ACO Optimizasyonu ({self.strategy.upper()})")

        for i in progress_bar:
            all_solutions = []
            iteration_best_cost = float('inf')
            iteration_best_solution = ([], iteration_best_cost)

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
                    
                    if self.strategy == "mmas":
                        self.pheromone_max = 1 / (self.mmas_rho * self.global_best_cost)
                        n = len(self.nodes_info)
                        p_best = 0.05 
                        if (n/2 - 1) > 0:
                            self.pheromone_min = self.pheromone_max * (1 - (p_best ** (1/n))) / ((n/2 - 1) * (p_best ** (1/n)))
                        else:
                            self.pheromone_min = self.pheromone_max * 0.05
                        
                        if not self.mmas_initialized:
                            print("\nİlk çözüm bulundu. MMAS feromonları τ_max'a ayarlanıyor...")
                            for edge in self.pheromones:
                                self.pheromones[edge] = self.pheromone_max
                            self.mmas_initialized = True
                
                if total_cost < iteration_best_cost:
                    iteration_best_cost = total_cost
                    iteration_best_solution = (ant.tours, total_cost)

            if self.strategy == "eas":
                self._update_pheromones_eas(all_solutions) 
            elif self.strategy == "mmas":
                self._update_pheromones_mmas(iteration_best_solution)
            
            cost_history.append(self.global_best_cost)
            progress_bar.set_postfix({"En İyi Maliyet": f"{self.global_best_cost/1000:.2f} km-eşdeğeri"})
        
        self.distance_cache.save_to_disk()
        return self.global_best_solution, self.global_best_cost, cost_history