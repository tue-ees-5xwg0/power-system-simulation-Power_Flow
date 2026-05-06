import pytest

from power_system_simulation.graph_processing import (
    EdgeAlreadyDisabledError,
    GraphCycleError,
    GraphNotFullyConnectedError,
    GraphProcessor,
    IDNotFoundError,
    IDNotUniqueError,
    InputLengthDoesNotMatchError,
)


def test_valid_tree_initializes():
    GraphProcessor(
        vertex_ids=[0, 1, 2],
        edge_ids=[10, 11],
        edge_vertex_id_pairs=[(0, 1), (1, 2)],
        edge_enabled=[True, True],
        source_vertex_id=0,
    )


def test_duplicate_vertex_ids_raise_error():
    with pytest.raises(IDNotUniqueError):
        GraphProcessor(
            vertex_ids=[0, 1, 1],
            edge_ids=[10],
            edge_vertex_id_pairs=[(0, 1)],
            edge_enabled=[True],
            source_vertex_id=0,
        )


def test_duplicate_edge_ids_raise_error():
    with pytest.raises(IDNotUniqueError):
        GraphProcessor(
            vertex_ids=[0, 1, 2],
            edge_ids=[10, 10],
            edge_vertex_id_pairs=[(0, 1), (1, 2)],
            edge_enabled=[True, True],
            source_vertex_id=0,
        )


def test_edge_pair_length_mismatch_raises_error():
    with pytest.raises(InputLengthDoesNotMatchError):
        GraphProcessor(
            vertex_ids=[0, 1, 2],
            edge_ids=[10, 11],
            edge_vertex_id_pairs=[(0, 1)],
            edge_enabled=[True, True],
            source_vertex_id=0,
        )


def test_edge_enabled_length_mismatch_raises_error():
    with pytest.raises(InputLengthDoesNotMatchError):
        GraphProcessor(
            vertex_ids=[0, 1, 2],
            edge_ids=[10, 11],
            edge_vertex_id_pairs=[(0, 1), (1, 2)],
            edge_enabled=[True],
            source_vertex_id=0,
        )


def test_invalid_edge_vertex_id_raises_error():
    with pytest.raises(IDNotFoundError):
        GraphProcessor(
            vertex_ids=[0, 1],
            edge_ids=[10],
            edge_vertex_id_pairs=[(0, 99)],
            edge_enabled=[True],
            source_vertex_id=0,
        )


def test_invalid_source_vertex_id_raises_error():
    with pytest.raises(IDNotFoundError):
        GraphProcessor(
            vertex_ids=[0, 1],
            edge_ids=[10],
            edge_vertex_id_pairs=[(0, 1)],
            edge_enabled=[True],
            source_vertex_id=99,
        )


def test_disconnected_graph_raises_error():
    with pytest.raises(GraphNotFullyConnectedError):
        GraphProcessor(
            vertex_ids=[0, 1, 2],
            edge_ids=[10],
            edge_vertex_id_pairs=[(0, 1)],
            edge_enabled=[True],
            source_vertex_id=0,
        )


def test_cycle_graph_raises_error():
    with pytest.raises(GraphCycleError):
        GraphProcessor(
            vertex_ids=[0, 1, 2],
            edge_ids=[10, 11, 12],
            edge_vertex_id_pairs=[(0, 1), (1, 2), (2, 0)],
            edge_enabled=[True, True, True],
            source_vertex_id=0,
        )


def test_valid_minimal_graph():
    GraphProcessor(
        vertex_ids=[0],
        edge_ids=[],
        edge_vertex_id_pairs=[],
        edge_enabled=[],
        source_vertex_id=0,
    )


def test_valid_with_disabled_extra_edge():
    GraphProcessor(
        vertex_ids=[0, 1, 2],
        edge_ids=[10, 11, 12],
        edge_vertex_id_pairs=[(0, 1), (1, 2), (0, 2)],
        edge_enabled=[True, True, False],
        source_vertex_id=0,
    )


def test_disconnected_due_to_disabled_edge_raises_error():
    with pytest.raises(GraphNotFullyConnectedError):
        GraphProcessor(
            vertex_ids=[0, 1, 2],
            edge_ids=[10, 11],
            edge_vertex_id_pairs=[(0, 1), (1, 2)],
            edge_enabled=[True, False],
            source_vertex_id=0,
        )


def test_downstream_docstring_example():
    gp = GraphProcessor(
        vertex_ids=[0, 2, 4],
        edge_ids=[1, 3],
        edge_vertex_id_pairs=[(0, 2), (2, 4)],
        edge_enabled=[True, True],
        source_vertex_id=0,
    )

    assert gp.find_downstream_vertices(1) == [2, 4]
    assert gp.find_downstream_vertices(3) == [4]


def test_downstream_disabled_edge_returns_empty():
    gp = GraphProcessor(
        vertex_ids=[0, 2, 4],
        edge_ids=[1, 3, 7],
        edge_vertex_id_pairs=[(0, 2), (2, 4), (0, 4)],
        edge_enabled=[True, True, False],
        source_vertex_id=0,
    )

    assert gp.find_downstream_vertices(7) == []


def test_downstream_nonexistent_edge_raises_error():
    gp = GraphProcessor(
        vertex_ids=[0, 2, 4],
        edge_ids=[1, 3],
        edge_vertex_id_pairs=[(0, 2), (2, 4)],
        edge_enabled=[True, True],
        source_vertex_id=0,
    )

    with pytest.raises(IDNotFoundError):
        gp.find_downstream_vertices(999)


def test_find_alternative_edges_docstring_example():
    gp = GraphProcessor(
        vertex_ids=[0, 2, 4, 6, 10],
        edge_ids=[1, 3, 5, 7, 8, 9],
        edge_vertex_id_pairs=[
            (0, 2),
            (0, 4),
            (0, 6),
            (2, 4),
            (4, 6),
            (2, 10),
        ],
        edge_enabled=[True, True, True, False, False, True],
        source_vertex_id=0,
    )

    assert gp.find_alternative_edges(1) == [7]
    assert gp.find_alternative_edges(3) == [7, 8]
    assert gp.find_alternative_edges(5) == [8]
    assert gp.find_alternative_edges(9) == []


def test_find_alternative_edges_nonexistent_edge_raises_error():
    gp = GraphProcessor(
        vertex_ids=[0, 1],
        edge_ids=[10],
        edge_vertex_id_pairs=[(0, 1)],
        edge_enabled=[True],
        source_vertex_id=0,
    )

    with pytest.raises(IDNotFoundError):
        gp.find_alternative_edges(999)


def test_find_alternative_edges_disabled_edge_raises_error():
    gp = GraphProcessor(
        vertex_ids=[0, 1, 2],
        edge_ids=[10, 11, 12],
        edge_vertex_id_pairs=[(0, 1), (1, 2), (0, 2)],
        edge_enabled=[True, True, False],
        source_vertex_id=0,
    )

    with pytest.raises(EdgeAlreadyDisabledError):
        gp.find_alternative_edges(12)


def test_find_alternative_edges_no_disabled_edges_returns_empty():
    gp = GraphProcessor(
        vertex_ids=[0, 1, 2],
        edge_ids=[10, 11],
        edge_vertex_id_pairs=[(0, 1), (1, 2)],
        edge_enabled=[True, True],
        source_vertex_id=0,
    )

    assert gp.find_alternative_edges(10) == []


def test_downstream_tree_edge_where_left_endpoint_is_downstream():
    gp = GraphProcessor(
        vertex_ids=[100, 101, 102],
        edge_ids=[1, 2],
        edge_vertex_id_pairs=[(100, 101), (101, 102)],
        edge_enabled=[True, True],
        source_vertex_id=102,
    )

    assert gp.find_downstream_vertices(1) == [100]


def test_downstream_universal_same_as_tree_for_cut_edge():
    gp = GraphProcessor(
        vertex_ids=[0, 2, 4],
        edge_ids=[1, 3],
        edge_vertex_id_pairs=[(0, 2), (2, 4)],
        edge_enabled=[True, True],
        source_vertex_id=0,
    )

    assert gp.find_downstream_vertices_universal(1) == [2, 4]
    assert gp.find_downstream_vertices_universal(3) == [4]


def test_downstream_universal_disabled_edge_returns_empty():
    gp = GraphProcessor(
        vertex_ids=[0, 1, 2],
        edge_ids=[10, 11, 12],
        edge_vertex_id_pairs=[(0, 1), (1, 2), (0, 2)],
        edge_enabled=[True, True, False],
        source_vertex_id=0,
    )

    assert gp.find_downstream_vertices_universal(12) == []


def test_downstream_universal_nonexistent_edge_raises_error():
    gp = GraphProcessor(
        vertex_ids=[0, 1],
        edge_ids=[10],
        edge_vertex_id_pairs=[(0, 1)],
        edge_enabled=[True],
        source_vertex_id=0,
    )

    with pytest.raises(IDNotFoundError):
        gp.find_downstream_vertices_universal(999)


def test_find_alternative_edges_returns_valid_disabled_edge():
    gp = GraphProcessor(
        vertex_ids=[0, 1, 2],
        edge_ids=[10, 11, 12],
        edge_vertex_id_pairs=[(0, 1), (1, 2), (0, 2)],
        edge_enabled=[True, True, False],
        source_vertex_id=0,
    )

    assert gp.find_alternative_edges(10) == [12]
