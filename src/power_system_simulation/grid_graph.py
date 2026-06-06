"""Build an Assignment 1 GraphProcessor from PGM input data."""

from power_grid_model import ComponentType

from power_system_simulation.graph_processing import GraphProcessor


def build_graph_processor(input_data: dict) -> GraphProcessor:
    """Turn the PGM nodes, lines and transformer into a GraphProcessor."""
    nodes = input_data[ComponentType.node]
    lines = input_data[ComponentType.line]
    transformer = input_data[ComponentType.transformer][0]

    vertex_ids = [int(node_id) for node_id in nodes["id"]]

    # The transformer and the lines are the edges. An edge is on only if both sides are connected.
    edge_ids = [int(transformer["id"])]
    edge_vertex_id_pairs = [(int(transformer["from_node"]), int(transformer["to_node"]))]
    edge_enabled = [bool(transformer["from_status"] and transformer["to_status"])]

    for line in lines:
        edge_ids.append(int(line["id"]))
        edge_vertex_id_pairs.append((int(line["from_node"]), int(line["to_node"])))
        edge_enabled.append(bool(line["from_status"] and line["to_status"]))

    return GraphProcessor(
        vertex_ids=vertex_ids,
        edge_ids=edge_ids,
        edge_vertex_id_pairs=edge_vertex_id_pairs,
        edge_enabled=edge_enabled,
        source_vertex_id=int(transformer["from_node"]),
    )
