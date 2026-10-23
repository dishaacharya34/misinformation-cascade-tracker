import pandas as pd
import networkx as nx


def analyze_influence(df: pd.DataFrame, columns: dict) -> dict:
    post_id_col = columns.get("post_id")
    parent_col = columns.get("parent_id")
    user_col = columns.get("user_id")

    if not post_id_col or not parent_col:
        return {
            "available": False,
            "reason": "Influence analysis requires post IDs and parent IDs.",
        }

    if not user_col:
        return {
            "available": False,
            "reason": "No user or author column was detected.",
        }

    working = df.dropna(subset=[post_id_col]).copy()
    working[post_id_col] = working[post_id_col].astype(str).str.strip()

    if working[post_id_col].duplicated().any():
        return {
            "available": False,
            "reason": "Post IDs must be unique for influence analysis.",
        }

    working = working[
        working[user_col].notna()
        & (working[user_col].astype(str).str.strip() != "")
    ]

    known_ids = set(working[post_id_col])
    graph = nx.DiGraph()
    graph.add_nodes_from(known_ids)

    for _, row in working.iterrows():
        parent_id = row[parent_col]
        post_id = row[post_id_col]

        if pd.notna(parent_id) and str(parent_id).strip() in known_ids:
            parent_id = str(parent_id).strip()
            if parent_id != post_id:
                graph.add_edge(parent_id, post_id)

    # Exclude cyclic edges so propagation metrics remain interpretable.
    if not nx.is_directed_acyclic_graph(graph):
        for cycle in list(nx.simple_cycles(graph)):
            if len(cycle) > 1:
                graph.remove_edge(cycle[-1], cycle[0])

    author_by_post = dict(
        zip(working[post_id_col], working[user_col].astype(str))
    )

    user_graph = nx.DiGraph()
    for parent_id, child_id in graph.edges():
        parent_user = author_by_post.get(parent_id)
        child_user = author_by_post.get(child_id)

        if parent_user and child_user and parent_user != child_user:
            if user_graph.has_edge(parent_user, child_user):
                user_graph[parent_user][child_user]["weight"] += 1
            else:
                user_graph.add_edge(
                    parent_user, child_user, weight=1
                )

    if user_graph.number_of_nodes() == 0:
        return {
            "available": True,
            "user_count": 0,
            "influential_users": [],
            "note": "No cross-user propagation links were found.",
        }

    centrality = nx.in_degree_centrality(user_graph)
    top_users = sorted(
        centrality.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:10]

    return {
        "available": True,
        "user_count": user_graph.number_of_nodes(),
        "propagation_links": user_graph.number_of_edges(),
        "influential_users": [
            {
                "user_id": str(user),
                "in_degree_centrality": round(float(score), 4),
                "incoming_propagation_links": int(
                    user_graph.in_degree(user)
                ),
            }
            for user, score in top_users
        ],
        "note": (
            "Influence reflects observed propagation links in this dataset, "
            "not verified real-world influence."
        ),
    }
