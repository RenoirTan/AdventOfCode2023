import random

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


Graph = dict[str, list[str]]


def merge_nodes(graph: Graph, a: str, b: str) -> Graph:
    """
    Remove all references to b and transfer edges to and from b to a.
    The graph is modified in-place.
    """
    if b not in graph:
        return graph
    b_neighbors = graph[b]
    del graph[b]
    for dest in b_neighbors:
        graph[dest] = [n if n != b else a for n in graph[dest]]
    return graph


def combine_dests(graph: Graph, a: str, b: str, new_node: str) -> Graph:
    graph[new_node] = (
        [d for d in graph.get(a, []) if d != b]
        + [d for d in graph.get(b, []) if d != a]
    )
    return graph


class Problem25(Problem):
    def __init__(self, graph: Graph):
        self.graph = graph
    
    @classmethod
    def from_str(cls, input: str) -> "Problem25":
        graph = Graph()
        
        def add_connection(src: str, dest: str):
            src_adj = graph.get(src, [])
            src_adj.append(dest)
            graph[src] = src_adj
        
        for line in input.splitlines():
            colon_index = line.find(":")
            src = line[:colon_index]
            dests = line[colon_index + 2:].strip().split(" ")
            for dest in dests:
                add_connection(src, dest)
                add_connection(dest, src)
        return Problem25(graph)
    
    def copy_graph(self) -> Graph:
        return {k: v.copy() for k, v in self.graph.items()}


class Solution25(Solution):
    def p1(self, problem: Problem25):
        while True:
            graph = problem.copy_graph()
            # number of primordial nodes contained in this node
            counts = {n: 1 for n in graph.keys()}
            while len(graph) > 2:
                a = random.choice(list(graph.keys()))
                b = random.choice(list(graph[a]))
                new_node = f"{a}/{b}"
                counts[new_node] = counts.get(a, 0) + counts.get(b, 0)
                combine_dests(graph, a, b, new_node)
                merge_nodes(graph, new_node, a)
                merge_nodes(graph, new_node, b)
            a, b = tuple(graph.keys())
            if len(graph[a]) == 3:
                return counts[a] * counts[b]
    
    def p2(self, problem: Problem25) -> int:
        return 100