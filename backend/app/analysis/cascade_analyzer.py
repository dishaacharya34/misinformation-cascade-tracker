import pandas as pd
import networkx as nx


def analyze_cascades(df: pd.DataFrame, columns: dict) -> dict:
    parent_col = columns.get("parent_id")
    post_id_col = columns.get("post_id")
    timestamp_col = columns.get("timestamp")

    if not parent_col or not post_id_col:
        return {
            "available": False,
            "reason": (
                "Cascade analysis requires both post ID and parent ID columns."
            ),
        }

    working = df.copy()
    working[post_id_col] = working[post_id_col].astype("string").str.strip()
    working[parent_col] = working[parent_col].astype("string").str.strip()

    working = working.dropna(subset=[post_id_col])
    working = working[working[post_id_col] != ""]

    if working[post_id_col].duplicated().any():
        return {
            "available": False,
            "reason": "Post IDs must be unique for reliable cascade analysis.",
        }

    known_ids = set(working[post_id_col].dropna())
    graph = nx.DiGraph()
    graph.add_nodes_from(known_ids)

    for _, row in working.iterrows():
        post_id = row[post_id_col]
        parent_id = row[parent_col]

        if pd.notna(parent_id) and parent_id not in ("", " <NA>"):
            if parent_id in known_ids and parent_id != post_id:
                graph.add_edge(parent_id, post_id)

    # Remove edges that would create cycles.
    cyclic_edges = list(nx.find_cycle(graph)) if not nx.is_directed_acyclic_graph(graph) else []
    if cyclic_edges:
        graph.remove_edges_from(cyclic_edges)

    components = []
    for nodes in nx.weakly_connected_components(graph):
        subgraph = graph.subgraph(nodes)
        roots = [node for node in nodes if subgraph.in_degree(node) == 0]

        if not roots:
            continue

        root = sorted(roots, key=str)[0]
        reachable = nx.descendants(subgraph, root) | {root}
        cascade = subgraph.subgraph(reachable)

        depths = nx.single_source_shortest_path_length(cascade, root)
        item = {
            "root_post_id": str(root),
            "size": int(cascade.number_of_nodes()),
            "edges": int(cascade.number_of_edges()),
            "depth": int(max(depths.values(), default=0)),
        }

        if timestamp_col:
            timestamps = pd.to_datetime(
                working.set_index(post_id_col)[timestamp_col],
                errors="coerce",
                utc=True,
            )
            cascade_times = timestamps.reindex(list(cascade.nodes())).dropna()

            if len(cascade_times) >= 2:
                duration = (
                    cascade_times.max() - cascade_times.min()
                ).total_seconds() / 3600

                item["duration_hours"] = round(duration, 3)
                item["posts_per_hour"] = (
                    round((len(cascade_times) - 1) / duration, 3)
                    if duration > 0 else None
                )
            else:
                item["duration_hours"] = None
                item["posts_per_hour"] = None

        components.append(item)

    components.sort(key=lambda item: item["size"], reverse=True)

    return {
        "available": True,
        "post_count": int(graph.number_of_nodes()),
        "edge_count": int(graph.number_of_edges()),
        "cascade_count": len(components),
        "cascades": components,
    }
