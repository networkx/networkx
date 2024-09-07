import pandas as pd

import networkx as nx


def fetch_drug_interaction_network():
    # Drug-drug interaction network
    # https://snap.stanford.edu/biodata/datasets/10001/10001-ChCh-Miner.html
    data = pd.read_csv(
        "https://snap.stanford.edu/biodata/datasets/10001/files/ChCh-Miner_durgbank-chem-chem.tsv.gz",
        sep="\t",
        header=None,
    )
    return nx.from_pandas_edgelist(data, source=0, target=1)
