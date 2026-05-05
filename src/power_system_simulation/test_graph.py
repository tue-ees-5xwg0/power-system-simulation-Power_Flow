"""
Test suite for GraphProcessor.

Run with:
    python3 -m unittest test_graph.py -v
"""

import unittest

from graph_processing import (
    GraphProcessor,
    IDNotFoundError,
    IDNotUniqueError,
    InputLengthDoesNotMatchError,
    GraphNotFullyConnectedError,
    GraphCycleError,
    EdgeAlreadyDisabledError,
)


# =============================================================================
# Init validation tests
# =============================================================================

class TestInitValidation(unittest.TestCase):
    """Tests for the input validation in __init__."""

    def test_duplicate_vertex_ids_raises(self):
        with self.assertRaises(IDNotUniqueError):
            GraphProcessor(
                vertex_ids=[0, 1, 1, 2],
                edge_ids=[10, 11, 12],
                edge_vertex_id_pairs=[(0, 1), (1, 2), (0, 2)],
                edge_enabled=[True, True, True],
                source_vertex_id=0,
            )

    def test_duplicate_edge_ids_raises(self):
        with self.assertRaises(IDNotUniqueError):
            GraphProcessor(
                vertex_ids=[0, 1, 2],
                edge_ids=[10, 10, 12],
                edge_vertex_id_pairs=[(0, 1), (1, 2), (0, 2)],
                edge_enabled=[True, True, False],
                source_vertex_id=0,
            )

    def test_edge_pairs_length_mismatch_raises(self):
        with self.assertRaises(InputLengthDoesNotMatchError):
            GraphProcessor(
                vertex_ids=[0, 1, 2],
                edge_ids=[10, 11],
                edge_vertex_id_pairs=[(0, 1)],  # only 1 pair for 2 edge ids
                edge_enabled=[True, True],
                source_vertex_id=0,
            )

    def test_edge_enabled_length_mismatch_raises(self):
        with self.assertRaises(InputLengthDoesNotMatchError):
            GraphProcessor(
                vertex_ids=[0, 1, 2],
                edge_ids=[10, 11],
                edge_vertex_id_pairs=[(0, 1), (1, 2)],
                edge_enabled=[True],  # only 1 flag for 2 edges
                source_vertex_id=0,
            )

    def test_edge_references_unknown_vertex_raises(self):
        with self.assertRaises(IDNotFoundError):
            GraphProcessor(
                vertex_ids=[0, 1, 2],
                edge_ids=[10, 11],
                edge_vertex_id_pairs=[(0, 1), (1, 99)],  # 99 doesn't exist
                edge_enabled=[True, True],
                source_vertex_id=0,
            )

    def test_unknown_source_vertex_raises(self):
        with self.assertRaises(IDNotFoundError):
            GraphProcessor(
                vertex_ids=[0, 1, 2],
                edge_ids=[10, 11],
                edge_vertex_id_pairs=[(0, 1), (1, 2)],
                edge_enabled=[True, True],
                source_vertex_id=42,  # not in vertex_ids
            )

    def test_disconnected_graph_raises(self):
        # Two components: {0,1} and {2,3}, no edge between them
        with self.assertRaises(GraphNotFullyConnectedError):
            GraphProcessor(
                vertex_ids=[0, 1, 2, 3],
                edge_ids=[10, 11],
                edge_vertex_id_pairs=[(0, 1), (2, 3)],
                edge_enabled=[True, True],
                source_vertex_id=0,
            )

    def test_disconnected_due_to_disabled_edge_raises(self):
        # Bridge edge between components is disabled, breaking connectivity
        with self.assertRaises(GraphNotFullyConnectedError):
            GraphProcessor(
                vertex_ids=[0, 1, 2],
                edge_ids=[10, 11],
                edge_vertex_id_pairs=[(0, 1), (1, 2)],
                edge_enabled=[True, False],  # vertex 2 is now unreachable
                source_vertex_id=0,
            )

    def test_cycle_raises(self):
        # Triangle: 3 vertices, 3 enabled edges, but a tree needs only 2
        with self.assertRaises(GraphCycleError):
            GraphProcessor(
                vertex_ids=[0, 1, 2],
                edge_ids=[10, 11, 12],
                edge_vertex_id_pairs=[(0, 1), (1, 2), (0, 2)],
                edge_enabled=[True, True, True],
                source_vertex_id=0,
            )

    def test_valid_minimal_graph(self):
        # Single vertex, no edges -- vacuously a tree (V=1, E=0 = V-1)
        gp = GraphProcessor(
            vertex_ids=[0],
            edge_ids=[],
            edge_vertex_id_pairs=[],
            edge_enabled=[],
            source_vertex_id=0,
        )
        self.assertIsNotNone(gp)

    def test_valid_with_disabled_extra_edge(self):
        # Tree of 3 vertices + 1 disabled cycle-forming edge -- still valid
        gp = GraphProcessor(
            vertex_ids=[0, 1, 2],
            edge_ids=[10, 11, 12],
            edge_vertex_id_pairs=[(0, 1), (1, 2), (0, 2)],
            edge_enabled=[True, True, False],  # disabled edge breaks the cycle
            source_vertex_id=0,
        )
        self.assertIsNotNone(gp)


# =============================================================================
# find_downstream_vertices: simple cases
# =============================================================================

class TestDownstreamSimple(unittest.TestCase):
    """Linear graph from the docstring example."""

    def setUp(self):
        # vertex_0 (source) --edge_1-- vertex_2 --edge_3-- vertex_4
        self.gp = GraphProcessor(
            vertex_ids=[0, 2, 4],
            edge_ids=[1, 3],
            edge_vertex_id_pairs=[(0, 2), (2, 4)],
            edge_enabled=[True, True],
            source_vertex_id=0,
        )

    def test_edge_near_source(self):
        # Cutting edge_1 leaves [2, 4] downstream
        self.assertEqual(sorted(self.gp.find_downstream_vertices(1)), [2, 4])

    def test_edge_at_leaf(self):
        # Cutting edge_3 leaves only [4] downstream
        self.assertEqual(sorted(self.gp.find_downstream_vertices(3)), [4])

    def test_nonexistent_edge_raises(self):
        with self.assertRaises(IDNotFoundError):
            self.gp.find_downstream_vertices(999)


# =============================================================================
# find_downstream_vertices: branching tree
# =============================================================================

class TestDownstreamBranching(unittest.TestCase):
    """
    Star-with-tails topology:

                vertex_0 (source)
               /     |       \
           edge_1  edge_2   edge_3
            /        |         \
        vertex_1  vertex_2   vertex_3
                    |          |
                  edge_4     edge_5
                    |          |
                vertex_4    vertex_5
    """

    def setUp(self):
        self.gp = GraphProcessor(
            vertex_ids=[0, 1, 2, 3, 4, 5],
            edge_ids=[1, 2, 3, 4, 5],
            edge_vertex_id_pairs=[(0, 1), (0, 2), (0, 3), (2, 4), (3, 5)],
            edge_enabled=[True, True, True, True, True],
            source_vertex_id=0,
        )

    def test_edge_to_leaf(self):
        # edge_1 connects source to leaf vertex_1
        self.assertEqual(sorted(self.gp.find_downstream_vertices(1)), [1])

    def test_edge_with_subtree(self):
        # edge_2 is source -> vertex_2, and vertex_2 has a child vertex_4
        self.assertEqual(sorted(self.gp.find_downstream_vertices(2)), [2, 4])

    def test_another_subtree(self):
        # edge_3 is source -> vertex_3, and vertex_3 has child vertex_5
        self.assertEqual(sorted(self.gp.find_downstream_vertices(3)), [3, 5])

    def test_deep_edge(self):
        # edge_4 is vertex_2 -> vertex_4 (a leaf)
        self.assertEqual(sorted(self.gp.find_downstream_vertices(4)), [4])


# =============================================================================
# find_downstream_vertices: larger graph with disabled edges
# =============================================================================

class TestDownstreamWithDisabled(unittest.TestCase):
    """
    Graph from the find_alternative_edges docstring:

    vertex_0 (source) --edge_1-- vertex_2 --edge_9-- vertex_10
             |                       |
             |                   edge_7 (disabled)
             |                       |
             ------edge_3---------- vertex_4
             |                       |
             |                   edge_8 (disabled)
             |                       |
             ------edge_5---------- vertex_6
    """

    def setUp(self):
        self.gp = GraphProcessor(
            vertex_ids=[0, 2, 4, 6, 10],
            edge_ids=[1, 3, 5, 7, 8, 9],
            edge_vertex_id_pairs=[
                (0, 2),    # edge_1
                (0, 4),    # edge_3
                (0, 6),    # edge_5
                (2, 4),    # edge_7 (disabled)
                (4, 6),    # edge_8 (disabled)
                (2, 10),   # edge_9
            ],
            edge_enabled=[True, True, True, False, False, True],
            source_vertex_id=0,
        )

    def test_edge_1_downstream(self):
        # Cutting edge_1: vertex_2's subtree is {2, 10}
        self.assertEqual(sorted(self.gp.find_downstream_vertices(1)), [2, 10])

    def test_edge_3_downstream(self):
        # Cutting edge_3: only vertex_4 hangs off (edge_7 and edge_8 are disabled)
        self.assertEqual(sorted(self.gp.find_downstream_vertices(3)), [4])

    def test_edge_5_downstream(self):
        # Cutting edge_5: only vertex_6 hangs off
        self.assertEqual(sorted(self.gp.find_downstream_vertices(5)), [6])

    def test_edge_9_downstream(self):
        # Cutting edge_9: vertex_10 is a leaf hanging off vertex_2
        self.assertEqual(sorted(self.gp.find_downstream_vertices(9)), [10])

    def test_disabled_edge_returns_empty(self):
        # edge_7 is disabled
        self.assertEqual(self.gp.find_downstream_vertices(7), [])

    def test_other_disabled_edge_returns_empty(self):
        # edge_8 is disabled
        self.assertEqual(self.gp.find_downstream_vertices(8), [])

    def test_nonexistent_edge_raises(self):
        with self.assertRaises(IDNotFoundError):
            self.gp.find_downstream_vertices(12345)


# =============================================================================
# find_downstream_vertices: deep linear chain (stress test)
# =============================================================================

class TestDownstreamDeepChain(unittest.TestCase):
    """
    Long chain: 0 -- 1 -- 2 -- 3 -- ... -- 49
    Stresses BFS on a deeper graph.
    """

    def setUp(self):
        n = 50
        vertex_ids = list(range(n))
        edge_ids = list(range(100, 100 + n - 1))  # 100, 101, ..., 148
        edge_pairs = [(i, i + 1) for i in range(n - 1)]
        edge_enabled = [True] * (n - 1)
        self.gp = GraphProcessor(
            vertex_ids=vertex_ids,
            edge_ids=edge_ids,
            edge_vertex_id_pairs=edge_pairs,
            edge_enabled=edge_enabled,
            source_vertex_id=0,
        )

    def test_first_edge(self):
        # Cutting edge 100 (between vertex 0 and 1) leaves vertices 1..49 downstream
        result = sorted(self.gp.find_downstream_vertices(100))
        self.assertEqual(result, list(range(1, 50)))

    def test_middle_edge(self):
        # Cutting edge 124 (between vertex 24 and 25) leaves vertices 25..49 downstream
        result = sorted(self.gp.find_downstream_vertices(124))
        self.assertEqual(result, list(range(25, 50)))

    def test_last_edge(self):
        # Cutting edge 148 (between vertex 48 and 49) leaves only [49] downstream
        result = sorted(self.gp.find_downstream_vertices(148))
        self.assertEqual(result, [49])


# =============================================================================
# find_downstream_vertices: source not at vertex 0
# =============================================================================

class TestDownstreamNonZeroSource(unittest.TestCase):
    """
    Same chain but source is in the middle. Confirms downstream is computed
    relative to source, not vertex_0.

        100 -- 101 -- 102 (source) -- 103 -- 104
    """

    def setUp(self):
        self.gp = GraphProcessor(
            vertex_ids=[100, 101, 102, 103, 104],
            edge_ids=[1, 2, 3, 4],
            edge_vertex_id_pairs=[(100, 101), (101, 102), (102, 103), (103, 104)],
            edge_enabled=[True, True, True, True],
            source_vertex_id=102,
        )

    def test_downstream_left_side(self):
        # edge_2 connects 101 and 102. Source is 102, so 101 (and 100) are downstream.
        self.assertEqual(sorted(self.gp.find_downstream_vertices(2)), [100, 101])

    def test_downstream_right_side(self):
        # edge_3 connects 102 and 103. Source is 102, so 103 (and 104) are downstream.
        self.assertEqual(sorted(self.gp.find_downstream_vertices(3)), [103, 104])

    def test_downstream_far_left(self):
        # edge_1 connects 100 and 101. Source is 102, so only 100 is downstream.
        self.assertEqual(sorted(self.gp.find_downstream_vertices(1)), [100])

    def test_downstream_far_right(self):
        # edge_4 connects 103 and 104. Source is 102, so only 104 is downstream.
        self.assertEqual(sorted(self.gp.find_downstream_vertices(4)), [104])



if __name__ == "__main__":
    unittest.main()
