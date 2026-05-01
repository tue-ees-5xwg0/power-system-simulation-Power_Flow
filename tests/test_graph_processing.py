import pytest

from power_system_simulation.graph_processing import (
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
