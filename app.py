# ============================================================
# MISINFORMATION CASCADE TRACKER
# ============================================================
#
# Project:
# Misinformation Cascade Tracker
#
# Pipeline:
#
# Data Input
#       ↓
# Preprocessing
#       ↓
# Misinformation Detection
#       ↓
# Cascade Graph Construction
#       ↓
# Propagation Analysis
#       ↓
# Influence Analysis
#       ↓
# Early-Risk Scoring
#       ↓
# Visualization
#
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

import re
import math
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


# ============================================================
# STREAMLIT CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Misinformation Cascade Tracker",
    page_icon="🕸️",
    layout="wide"
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

RAW_DIR = DATA_DIR / "raw"

PROCESSED_DIR = DATA_DIR / "processed"


# ============================================================
# REQUIRED DATASET COLUMNS
# ============================================================

REQUIRED_COLUMNS = [
    "post_id",
    "user_id",
    "parent_id",
    "timestamp",
    "text",
    "label"
]


# ============================================================
# LABEL CONVERSION
# ============================================================

LABEL_MAP = {

    "misinformation": 1,
    "false": 1,
    "fake": 1,
    "rumor": 1,
    "rumour": 1,
    "unverified": 1,

    "non-misinformation": 0,
    "non_misinformation": 0,
    "true": 0,
    "real": 0,
    "non-rumor": 0,
    "non_rumor": 0,
    "nonrumor": 0,

    "0": 0,
    "1": 1
}


# ============================================================
# PAGE HEADER
# ============================================================

st.title("🕸️ Misinformation Cascade Tracker")

st.markdown(
    """
    ### Graph-Based Framework for Propagation Analysis and Early-Risk Detection

    **Data → Preprocessing → Detection → Graph → Cascade Metrics
    → Influence → Risk → Visualization**
    """
)


# ============================================================
# TEXT PREPROCESSING
# ============================================================

def clean_text(text):

    if pd.isna(text):
        return ""

    text = str(text)

    # Lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(
        r"http\S+|www\.\S+",
        " ",
        text
    )

    # Remove mentions
    text = re.sub(
        r"@\w+",
        " ",
        text
    )

    # Remove hashtag symbol
    text = text.replace("#", "")

    # Remove special characters
    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    # Remove multiple spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# LABEL NORMALIZATION
# ============================================================

def normalize_label(value):

    if pd.isna(value):
        return np.nan

    value = str(value).strip().lower()

    if value in LABEL_MAP:
        return LABEL_MAP[value]

    try:
        return int(float(value))
    except:
        return np.nan


# ============================================================
# LOAD DATA
# ============================================================

def load_data(uploaded_file=None):

    # --------------------------------------------------------
    # If user uploads CSV
    # --------------------------------------------------------

    if uploaded_file is not None:

        df = pd.read_csv(uploaded_file)

    else:

        # Look for demo dataset
        demo_file = RAW_DIR / "demo_cascade.csv"

        if not demo_file.exists():

            # Also check data folder
            demo_file = DATA_DIR / "demo_cascade.csv"

        if not demo_file.exists():

            return pd.DataFrame()

        df = pd.read_csv(demo_file)


    # --------------------------------------------------------
    # Check columns
    # --------------------------------------------------------

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            "Your CSV is missing these columns: "
            + ", ".join(missing)
        )


    # --------------------------------------------------------
    # Copy dataset
    # --------------------------------------------------------

    df = df.copy()


    # --------------------------------------------------------
    # Clean text
    # --------------------------------------------------------

    df["text"] = (
        df["text"]
        .fillna("")
        .astype(str)
    )

    df["clean_text"] = (
        df["text"]
        .apply(clean_text)
    )


    # --------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )


    # --------------------------------------------------------
    # Label
    # --------------------------------------------------------

    df["label_binary"] = (
        df["label"]
        .apply(normalize_label)
    )


    # --------------------------------------------------------
    # IDs
    # --------------------------------------------------------

    df["post_id"] = (
        df["post_id"]
        .astype(str)
    )

    df["user_id"] = (
        df["user_id"]
        .astype(str)
    )


    # --------------------------------------------------------
    # Parent ID
    # --------------------------------------------------------

    df["parent_id"] = (
        df["parent_id"]
        .fillna("")
        .astype(str)
    )

    df["parent_id"] = (
        df["parent_id"]
        .replace(
            {
                "nan": "",
                "None": "",
                "none": ""
            }
        )
    )


    # --------------------------------------------------------
    # Remove duplicate posts
    # --------------------------------------------------------

    df = df.drop_duplicates(
        subset=["post_id"]
    )


    # --------------------------------------------------------
    # Remove rows without timestamp
    # --------------------------------------------------------

    df = df.dropna(
        subset=["timestamp"]
    )


    # --------------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------------

    df = (
        df
        .sort_values("timestamp")
        .reset_index(drop=True)
    )


    return df


# ============================================================
# MACHINE LEARNING CLASSIFIER
# ============================================================

def train_classifier(df):

    labelled = (
        df
        .dropna(
            subset=["label_binary"]
        )
        .copy()
    )


    # Need two classes
    if labelled["label_binary"].nunique() < 2:

        return None, None


    # Need enough records
    if len(labelled) < 6:

        return None, None


    # --------------------------------------------------------
    # Train-test split
    # --------------------------------------------------------

    try:

        X_train, X_test, y_train, y_test = train_test_split(

            labelled["clean_text"],

            labelled["label_binary"].astype(int),

            test_size=0.25,

            random_state=42,

            stratify=labelled["label_binary"]
        )

    except ValueError:

        X_train, X_test, y_train, y_test = train_test_split(

            labelled["clean_text"],

            labelled["label_binary"].astype(int),

            test_size=0.25,

            random_state=42
        )


    # ========================================================
    # TF-IDF + LOGISTIC REGRESSION
    # ========================================================

    model = Pipeline([

        (
            "tfidf",

            TfidfVectorizer(

                ngram_range=(1, 2),

                max_features=5000,

                sublinear_tf=True
            )
        ),

        (
            "classifier",

            LogisticRegression(

                max_iter=2000,

                class_weight="balanced",

                random_state=42
            )
        )
    ])


    # Train
    model.fit(
        X_train,
        y_train
    )


    # Test
    predictions = (
        model
        .predict(X_test)
    )


    # Metrics
    metrics = {

        "accuracy":
            accuracy_score(
                y_test,
                predictions
            ),

        "precision":
            precision_score(
                y_test,
                predictions,
                zero_division=0
            ),

        "recall":
            recall_score(
                y_test,
                predictions,
                zero_division=0
            ),

        "f1":
            f1_score(
                y_test,
                predictions,
                zero_division=0
            )
    }


    # Retrain using complete labelled data
    model.fit(

        labelled["clean_text"],

        labelled["label_binary"].astype(int)
    )


    return model, metrics


# ============================================================
# BUILD PROPAGATION GRAPH
# ============================================================

def build_graph(df):

    G = nx.DiGraph()


    # --------------------------------------------------------
    # Nodes
    # --------------------------------------------------------

    for _, row in df.iterrows():

        post_id = row["post_id"]

        G.add_node(

            post_id,

            user_id=row["user_id"],

            timestamp=row["timestamp"],

            text=row["text"],

            label=row["label_binary"]
        )


    # --------------------------------------------------------
    # Edges
    # --------------------------------------------------------

    for _, row in df.iterrows():

        child = row["post_id"]

        parent = row["parent_id"]


        if (

            parent != ""

            and

            parent in G.nodes

            and

            parent != child

        ):

            G.add_edge(
                parent,
                child
            )


    return G


# ============================================================
# FIND ROOT NODES
# ============================================================

def get_roots(G):

    return [

        node

        for node in G.nodes

        if G.in_degree(node) == 0
    ]


# ============================================================
# GET CASCADE
# ============================================================

def get_cascade(G, root):

    if root not in G:

        return G.copy()


    descendants = nx.descendants(
        G,
        root
    )


    nodes = (
        {root}
        |
        descendants
    )


    return G.subgraph(
        nodes
    ).copy()


# ============================================================
# CASCADE METRICS
# ============================================================

def calculate_metrics(G, root):

    cascade = get_cascade(
        G,
        root
    )


    size = cascade.number_of_nodes()


    if size == 0:

        return {
            "size": 0,
            "depth": 0,
            "duration": 0,
            "speed": 0,
            "growth": 0
        }


    # --------------------------------------------------------
    # Time
    # --------------------------------------------------------

    timestamps = [

        cascade.nodes[node]["timestamp"]

        for node in cascade.nodes

        if pd.notna(
            cascade.nodes[node]["timestamp"]
        )
    ]


    start = min(timestamps)

    end = max(timestamps)


    seconds = max(
        (end - start).total_seconds(),
        1
    )


    hours = seconds / 3600


    # --------------------------------------------------------
    # Depth
    # --------------------------------------------------------

    depths = nx.single_source_shortest_path_length(

        cascade,

        root
    )


    depth = max(
        depths.values()
    )


    # --------------------------------------------------------
    # Speed
    # --------------------------------------------------------

    events = max(
        size - 1,
        0
    )


    speed = events / hours


    # --------------------------------------------------------
    # Growth
    # --------------------------------------------------------

    growth = events / hours


    return {

        "size":
            int(size),

        "depth":
            int(depth),

        "duration":
            float(hours),

        "speed":
            float(speed),

        "growth":
            float(growth)
    }


# ============================================================
# INFLUENCE ANALYSIS
# ============================================================

def influence_analysis(G):

    if G.number_of_nodes() == 0:

        return pd.DataFrame()


    degree = dict(
        G.degree()
    )


    degree_centrality = (
        nx.degree_centrality(G)
    )


    betweenness = (
        nx.betweenness_centrality(
            G,
            normalized=True
        )
    )


    rows = []


    for node in G.nodes:

        rows.append({

            "post_id":
                node,

            "user_id":
                G.nodes[node]["user_id"],

            "degree":
                degree[node],

            "degree_centrality":
                degree_centrality[node],

            "betweenness_centrality":
                betweenness[node]
        })


    result = pd.DataFrame(
        rows
    )


    # Prototype influence measure
    result["influence"] = (

        0.6
        *
        result["degree_centrality"]

        +

        0.4
        *
        result["betweenness_centrality"]
    )


    return (

        result
        .sort_values(
            "influence",
            ascending=False
        )
        .reset_index(drop=True)
    )


# ============================================================
# RISK SCORE
# ============================================================

def calculate_risk(

    metrics,

    influence_df,

    growth_weight,

    speed_weight,

    influence_weight
):

    if influence_df.empty:

        max_influence = 0

    else:

        max_influence = float(

            influence_df[
                "influence"
            ].max()
        )


    # --------------------------------------------------------
    # Normalize growth
    # --------------------------------------------------------

    growth_normalized = (

        1
        -
        math.exp(
            -metrics["growth"] / 10
        )
    )


    # --------------------------------------------------------
    # Normalize speed
    # --------------------------------------------------------

    speed_normalized = (

        1
        -
        math.exp(
            -metrics["speed"] / 10
        )
    )


    # --------------------------------------------------------
    # Influence
    # --------------------------------------------------------

    influence_normalized = min(
        max(max_influence, 0),
        1
    )


    # --------------------------------------------------------
    # Weighted risk score
    # --------------------------------------------------------

    score = 100 * (

        growth_weight
        *
        growth_normalized

        +

        speed_weight
        *
        speed_normalized

        +

        influence_weight
        *
        influence_normalized
    )


    # --------------------------------------------------------
    # Risk category
    # --------------------------------------------------------

    if score >= 70:

        level = "High"

    elif score >= 40:

        level = "Medium"

    else:

        level = "Low"


    return {

        "score":
            score,

        "level":
            level,

        "growth":
            growth_normalized,

        "speed":
            speed_normalized,

        "influence":
            influence_normalized
    }


# ============================================================
# PROPAGATION GRAPH VISUALIZATION
# ============================================================

def draw_graph(

    G,

    root,

    influence_df
):

    fig, ax = plt.subplots(
        figsize=(12, 7)
    )


    # --------------------------------------------------------
    # Determine levels
    # --------------------------------------------------------

    levels = (
        nx
        .single_source_shortest_path_length(
            G,
            root
        )
    )


    groups = defaultdict(list)


    for node, level in levels.items():

        groups[level].append(
            node
        )


    # --------------------------------------------------------
    # Position nodes
    # --------------------------------------------------------

    positions = {}


    for level, nodes in groups.items():

        nodes = sorted(nodes)

        count = len(nodes)


        for index, node in enumerate(nodes):

            x = (

                index
                -
                (count - 1) / 2

            ) * 2


            y = -level * 2


            positions[node] = (
                x,
                y
            )


    # --------------------------------------------------------
    # Influence values
    # --------------------------------------------------------

    influence_map = {}


    if not influence_df.empty:

        influence_map = dict(

            zip(

                influence_df["post_id"],

                influence_df["influence"]
            )
        )


    # --------------------------------------------------------
    # Node sizes
    # --------------------------------------------------------

    sizes = []


    for node in G.nodes:

        if node == root:

            sizes.append(1500)

        else:

            sizes.append(

                400
                +
                1800
                *
                influence_map.get(
                    node,
                    0
                )
            )


    # --------------------------------------------------------
    # Edges
    # --------------------------------------------------------

    nx.draw_networkx_edges(

        G,

        positions,

        ax=ax,

        arrows=True,

        arrowsize=15,

        alpha=0.6
    )


    # --------------------------------------------------------
    # Nodes
    # --------------------------------------------------------

    colors = [

        1
        if node == root

        else influence_map.get(
            node,
            0
        )

        for node in G.nodes
    ]


    nx.draw_networkx_nodes(

        G,

        positions,

        ax=ax,

        node_size=sizes,

        node_color=colors,

        cmap="viridis",

        vmin=0,

        vmax=1,

        edgecolors="black"
    )


    # --------------------------------------------------------
    # Labels
    # --------------------------------------------------------

    labels = {}


    if not influence_df.empty:

        important = set(

            influence_df
            .head(8)["post_id"]
        )

    else:

        important = set()


    for node in G.nodes:

        if (

            node == root

            or node in important
        ):

            labels[node] = node


    nx.draw_networkx_labels(

        G,

        positions,

        labels=labels,

        font_size=9
    )


    ax.set_title(
        "Misinformation Propagation Graph"
    )


    ax.axis("off")


    fig.tight_layout()


    return fig


# ============================================================
# GROWTH GRAPH
# ============================================================

def draw_growth_graph(

    G,

    root
):

    cascade = get_cascade(
        G,
        root
    )


    timestamps = [

        cascade.nodes[node]["timestamp"]

        for node in cascade.nodes

        if pd.notna(
            cascade.nodes[node]["timestamp"]
        )
    ]


    timestamps.sort()


    start = min(
        timestamps
    )


    elapsed = [

        (
            timestamp
            -
            start
        ).total_seconds() / 3600

        for timestamp in timestamps
    ]


    sizes = list(
        range(
            1,
            len(elapsed) + 1
        )
    )


    fig, ax = plt.subplots(
        figsize=(10, 5)
    )


    ax.plot(

        elapsed,

        sizes,

        marker="o"
    )


    ax.set_xlabel(
        "Elapsed Time (hours)"
    )


    ax.set_ylabel(
        "Cascade Size"
    )


    ax.set_title(
        "Cascade Growth Over Time"
    )


    ax.grid(
        alpha=0.25
    )


    fig.tight_layout()


    return fig


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(
    "⚙️ Controls"
)


# Upload
uploaded_file = st.sidebar.file_uploader(

    "Upload CSV Dataset",

    type=["csv"]
)


st.sidebar.divider()


st.sidebar.subheader(
    "Early-Risk Weights"
)


growth_weight = st.sidebar.slider(

    "Growth Weight",

    0.0,

    1.0,

    0.4,

    0.05
)


speed_weight = st.sidebar.slider(

    "Speed Weight",

    0.0,

    1.0,

    0.3,

    0.05
)


influence_weight = st.sidebar.slider(

    "Influence Weight",

    0.0,

    1.0,

    0.3,

    0.05
)


total_weight = (

    growth_weight
    +
    speed_weight
    +
    influence_weight
)


st.sidebar.write(
    f"Total: {total_weight:.2f}"
)


# ============================================================
# LOAD DATA
# ============================================================

try:

    df = load_data(
        uploaded_file
    )

except Exception as error:

    st.error(
        str(error)
    )

    st.stop()


if df.empty:

    st.warning(

        """
        No dataset was found.

        Place demo_cascade.csv inside:

        data/raw/

        or upload a CSV using the sidebar.
        """
    )

    st.stop()


# ============================================================
# DATASET OVERVIEW
# ============================================================

st.header(
    "1. Dataset Overview"
)


c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "Posts",
    len(df)
)


c2.metric(
    "Users",
    df["user_id"].nunique()
)


c3.metric(

    "Interactions",

    int(
        (
            df["parent_id"]
            != ""
        ).sum()
    )
)


duration = (

    df["timestamp"].max()
    -
    df["timestamp"].min()
).total_seconds() / 3600


c4.metric(

    "Time Span",

    f"{duration:.2f} h"
)


with st.expander(
    "View Dataset"
):

    st.dataframe(
        df,
        use_container_width=True
    )


# ============================================================
# MISINFORMATION DETECTION
# ============================================================

st.header(
    "2. Misinformation Detection"
)


model, ml_metrics = train_classifier(
    df
)


if model is None:

    st.warning(
        "Not enough labelled data to train the classifier."
    )

else:

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    df["predicted_label"] = (

        model
        .predict(
            df["clean_text"]
        )
    )


    # --------------------------------------------------------
    # Probability
    # --------------------------------------------------------

    probabilities = (

        model
        .predict_proba(
            df["clean_text"]
        )
    )


    classes = list(

        model
        .named_steps[
            "classifier"
        ]
        .classes_
    )


    if 1 in classes:

        index = classes.index(1)

    else:

        index = 0


    df[
        "misinformation_confidence"
    ] = probabilities[:, index]


    # --------------------------------------------------------
    # Display metrics
    # --------------------------------------------------------

    m1, m2, m3, m4 = st.columns(4)


    m1.metric(
        "Accuracy",
        f"{ml_metrics['accuracy']:.3f}"
    )


    m2.metric(
        "Precision",
        f"{ml_metrics['precision']:.3f}"
    )


    m3.metric(
        "Recall",
        f"{ml_metrics['recall']:.3f}"
    )


    m4.metric(
        "F1 Score",
        f"{ml_metrics['f1']:.3f}"
    )


    st.info(

        """
        These metrics are calculated from the currently loaded
        labelled dataset. They are not claimed as official
        Twitter15/Twitter16 benchmark results.
        """
    )


# ============================================================
# GRAPH CONSTRUCTION
# ============================================================

st.header(
    "3. Cascade Graph Construction"
)


G = build_graph(
    df
)


roots = get_roots(
    G
)


if len(roots) == 0:

    st.error(
        "No root/source post was found."
    )

    st.stop()


selected_root = st.selectbox(

    "Select Source Post",

    roots
)


cascade = get_cascade(

    G,

    selected_root
)


# ============================================================
# METRICS
# ============================================================

metrics = calculate_metrics(

    G,

    selected_root
)


# ============================================================
# INFLUENCE
# ============================================================

influence_df = influence_analysis(
    cascade
)


# ============================================================
# PROPAGATION GRAPH
# ============================================================

st.subheader(
    "Misinformation Propagation Graph"
)


graph_figure = draw_graph(

    cascade,

    selected_root,

    influence_df
)


st.pyplot(
    graph_figure,
    use_container_width=True
)


# ============================================================
# PROPAGATION ANALYSIS
# ============================================================

st.header(
    "4. Propagation Analysis"
)


a, b, c, d, e = st.columns(5)


a.metric(
    "Cascade Size",
    metrics["size"]
)


b.metric(
    "Cascade Depth",
    metrics["depth"]
)


c.metric(
    "Duration",
    f"{metrics['duration']:.2f} h"
)


d.metric(
    "Propagation Speed",
    f"{metrics['speed']:.2f}/h"
)


e.metric(
    "Growth Rate",
    f"{metrics['growth']:.2f}/h"
)


# ============================================================
# CASCADE GROWTH
# ============================================================

st.subheader(
    "Cascade Growth Visualization"
)


growth_figure = draw_growth_graph(

    G,

    selected_root
)


st.pyplot(

    growth_figure,

    use_container_width=True
)


# ============================================================
# INFLUENCE
# ============================================================

st.header(
    "5. Influential Node Analysis"
)


if not influence_df.empty:

    st.dataframe(

        influence_df,

        use_container_width=True
    )


# ============================================================
# RISK SCORE
# ============================================================

st.header(
    "6. Early-Risk Scoring"
)


if abs(
    total_weight - 1
) > 0.001:

    st.error(
        "Risk weights must add up to 1.00."
    )

else:

    risk = calculate_risk(

        metrics,

        influence_df,

        growth_weight,

        speed_weight,

        influence_weight
    )


    r1, r2 = st.columns(2)


    r1.metric(

        "Risk Score",

        f"{risk['score']:.2f}/100"
    )


    r2.metric(

        "Risk Level",

        risk["level"]
    )


    st.progress(

        min(
            max(
                risk["score"] / 100,
                0
            ),
            1
        )
    )


    st.write(
        f"""
        Growth component: **{risk['growth']:.3f}**

        Speed component: **{risk['speed']:.3f}**

        Influence component: **{risk['influence']:.3f}**
        """
    )


    st.info(

        """
        This risk score is an analytical prioritization
        indicator. It is not a probability or a calibrated
        prediction.
        """
    )


# ============================================================
# SOURCE POST
# ============================================================

st.header(
    "7. Source Post Information"
)


source = (

    df[
        df["post_id"]
        ==
        selected_root
    ]
)


if not source.empty:

    source = source.iloc[0]


    col1, col2 = st.columns(2)


    with col1:

        st.write(
            "**Post ID:**",
            source["post_id"]
        )

        st.write(
            "**User ID:**",
            source["user_id"]
        )

        st.write(
            "**Timestamp:**",
            source["timestamp"]
        )


    with col2:

        st.write(
            "**Original Post:**"
        )

        st.write(
            source["text"]
        )


    if "predicted_label" in df.columns:

        prediction = int(
            source["predicted_label"]
        )


        confidence = float(

            source[
                "misinformation_confidence"
            ]
        )


        if prediction == 1:

            st.error(
                "Predicted: MISINFORMATION"
            )

        else:

            st.success(
                "Predicted: NON-MISINFORMATION"
            )


        st.write(
            f"Confidence: **{confidence:.2f}**"
        )


# ============================================================
# EXPORT
# ============================================================

st.header(
    "8. Export Results"
)


if abs(
    total_weight - 1
) <= 0.001:

    export_risk = risk["score"]

    export_level = risk["level"]

else:

    export_risk = np.nan

    export_level = "Invalid weights"


summary = pd.DataFrame({

    "Source Post": [
        selected_root
    ],

    "Cascade Size": [
        metrics["size"]
    ],

    "Cascade Depth": [
        metrics["depth"]
    ],

    "Duration Hours": [
        metrics["duration"]
    ],

    "Propagation Speed": [
        metrics["speed"]
    ],

    "Growth Rate": [
        metrics["growth"]
    ],

    "Risk Score": [
        export_risk
    ],

    "Risk Level": [
        export_level
    ]
})


st.dataframe(

    summary,

    use_container_width=True
)


csv_data = (

    summary
    .to_csv(
        index=False
    )
    .encode("utf-8")
)


st.download_button(

    "⬇️ Download Cascade Summary",

    data=csv_data,

    file_name="cascade_summary.csv",

    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Misinformation Cascade Tracker | Graph-Based Propagation Analysis"
)