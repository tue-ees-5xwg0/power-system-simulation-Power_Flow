"""
This is a skeleton for the graph processing assignment.

We define a graph processor class with some function skeletons.
"""

from typing import List, Tuple


class IDNotFoundError(Exception):
    pass


class InputLengthDoesNotMatchError(Exception):
    pass


class IDNotUniqueError(Exception):
    pass


class GraphNotFullyConnectedError(Exception):
    pass


class GraphCycleError(Exception):
    pass


class EdgeAlreadyDisabledError(Exception):
    pass


class GraphProcessor:
    """
    General documentation of this class.
    You need to describe the purpose of this class and the functions in it.
    We are using an undirected graph in the processor.
    """

    def __init__(
        self,
        vertex_ids: List[int],
        edge_ids: List[int],
        edge_vertex_id_pairs: List[Tuple[int, int]],
        edge_enabled: List[bool],
        source_vertex_id: int,
    ) -> None:
        # check vertex_id uniqueness
        # remove possible duplicates, if lengths don't match, duplicates were present
        if len(set(vertex_ids)) != len(vertex_ids): 
            raise IDNotUniqueError()

        # check edge_id uniqueness
        if len(set(edge_ids)) != len(edge_ids):
            raise IDNotUniqueError()
        
        # check if vertex_id_pairs has the same length as edge_id
        if len(vertex_id_pairs) != len(edge_id):
            raise InputLengthDoesNotMatchError()

        # check if edge_vertex_id_pairs contain valid vertex ids.
        self.vertex_set = set(vertex_ids) #use set for O(1) lookups
        for u, v in edge_vertex_id_pairs:
            if u not in self.vertex_set or v not in self.vertex_set:
                raise IDNotFoundError()

        # check if edge_enabled has same length as edge_ids
        if len(edge_enabled) != len(edge_ids):
            raise InputLengthDoesNotMatchError()

        # check if source_vertex_id is a valid vertex id
        if source_vertex_id not in self.vertex_set:
            raise IDNotFoundError() 

        # fixing internal graph presentation, idea is:
        # use adjacency list to allow for fast processing of graph: 
        # processing each vertex v takes O(degree(v)) time
        # BFS takes O(V+E) wcrt, here E = V - 1, so BFS runs in linear time
        self.adjacency_list = {v: [] for v in self.vertex_set}
        self.edge_map = {}          # which vertices an edge connects
        self.edge_enabled_map = {}  # is the edge enabled?
        
        #fill edge_map and edge_enabled_map
        for i, edge_id in enumerate(edge_ids):
            u, v = edge_vertex_id_pairs[i]
            self.edge_map[edge_id] = (u, v)
            self.edge_enabled_map[edge_id] = edge_enabled[i]
        
        #build adjacency list
        for edge_id, (u, v) in self.edge_map.items():
            if self.edge_enabled_map[edge_id]:
                self.adjacency_list[u].append((v, edge_id))
                self.adjacency_list[v].append((u, edge_id))

        # check if graph is fully connected
        # uses DFS to decide if the graph is fully connected,
        # if from any arbitrary vertex we can reach all other vertices
        # then the graph is fully connetced. 
        visited = set()
        for i in vertex_ids

        # check if graph contains cycles
        # a tree with v vertices must have v-1 edges, otherwise it is not valid. 
        enabled_edge_count = sum(self.edge_enabled_map.values())
        if enabled_edge_count != len(self.vertex_set) - 1:
            raise GraphCycleError()
        """
            6. The graph should be fully connected. (GraphNotFullyConnectedError)
        If one certain condition is not satisfied, the error in the parentheses should be raised.
        """
        pass

    def find_downstream_vertices(self, edge_id: int) -> List[int]:
        """
        Given an edge id, return all the vertices which are in the downstream of the edge,
            with respect to the source vertex.
            Including the downstream vertex of the edge itself!

        Only enabled edges should be taken into account in the analysis.
        If the given edge_id is a disabled edge, it should return empty list.
        If the given edge_id does not exist, it should raise IDNotFoundError.


        For example, given the following graph (all edges enabled):

            vertex_0 (source) --edge_1-- vertex_2 --edge_3-- vertex_4

        Call find_downstream_vertices with edge_id=1 will return [2, 4]
        Call find_downstream_vertices with edge_id=3 will return [4]

        Args:
            edge_id: edge id to be searched

        Returns:
            A list of all downstream vertices.
        """
        # put your implementation here
        pass

    def find_alternative_edges(self, disabled_edge_id: int) -> List[int]:
        """
        Given an enabled edge, do the following analysis:
            If the edge is going to be disabled,
                which (currently disabled) edge can be enabled to ensure
                that the graph is again fully connected and acyclic?
            Return a list of all alternative edges.
        If the disabled_edge_id is not a valid edge id, it should raise IDNotFoundError.
        If the disabled_edge_id is already disabled, it should raise EdgeAlreadyDisabledError.
        If there are no alternative to make the graph fully connected again, it should return empty list.


        For example, given the following graph:

        vertex_0 (source) --edge_1(enabled)-- vertex_2 --edge_9(enabled)-- vertex_10
                 |                               |
                 |                           edge_7(disabled)
                 |                               |
                 -----------edge_3(enabled)-- vertex_4
                 |                               |
                 |                           edge_8(disabled)
                 |                               |
                 -----------edge_5(enabled)-- vertex_6

        Call find_alternative_edges with disabled_edge_id=1 will return [7]
        Call find_alternative_edges with disabled_edge_id=3 will return [7, 8]
        Call find_alternative_edges with disabled_edge_id=5 will return [8]
        Call find_alternative_edges with disabled_edge_id=9 will return []

        Args:
            disabled_edge_id: edge id (which is currently enabled) to be disabled

        Returns:
            A list of alternative edge ids.
        """
        # put your implementation here
        pass
