"""Neural Overlapping Community Detection (NOCD) building blocks.

This module imports torch and torch_geometric and must only be loaded lazily
from :func:`nocd_communities`.

References
----------
.. [1] Oleksandr Shchur and Stephan Günnemann.
   Overlapping Community Detection with Graph Neural Networks.
   Deep Learning on Graphs Workshop, KDD (2019).
   https://arxiv.org/abs/1909.12201
"""

from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch import nn
from torch_geometric.nn import GCNConv
from torch_geometric.utils import from_scipy_sparse_matrix


class CSRGraphDataset:
    """CSR adjacency matrix as a PyTorch Geometric-style graph dataset."""

    def __init__(
        self,
        adjacency_csr,
        node_features=None,
        node_labels=None,
        validate: bool = True,
    ):
        self.adj_csr = adjacency_csr
        self.num_nodes = adjacency_csr.shape[0]
        self.num_edges = adjacency_csr.nnz

        if validate:
            self._validate_graph()

        self.edge_index, self.edge_weights = from_scipy_sparse_matrix(adjacency_csr)

        if node_features is not None:
            self.node_features = torch.FloatTensor(node_features)
        else:
            self.node_features = torch.FloatTensor(adjacency_csr.toarray())

        self.node_features = F.normalize(self.node_features, p=2, dim=1)

        self.node_labels = node_labels
        self.feature_dim = self.node_features.shape[1]
        self.is_directed = not self._is_symmetric()

    def _validate_graph(self):
        if self.adj_csr.shape[0] != self.adj_csr.shape[1]:
            raise ValueError("Adjacency matrix must be square")
        if self.adj_csr.nnz == 0:
            raise ValueError("Graph must have edges")
        if np.any(self.adj_csr.data < 0):
            raise ValueError("Edge weights must be non-negative")

    def _is_symmetric(self) -> bool:
        diff = self.adj_csr - self.adj_csr.T
        return diff.nnz == 0

    def to_pyg_data(self):
        from torch_geometric.data import Data

        return Data(
            x=self.node_features,
            edge_index=self.edge_index,
            edge_attr=self.edge_weights,
            num_nodes=self.num_nodes,
        )

    def get_graph_stats(self) -> dict:
        degrees = np.array(self.adj_csr.sum(axis=1)).flatten()
        n = self.num_nodes
        density = self.num_edges / (n * (n - 1)) if n > 1 else 0.0
        return {
            "num_nodes": self.num_nodes,
            "num_edges": self.num_edges,
            "density": density,
            "avg_degree": float(degrees.mean()) if len(degrees) else 0.0,
            "max_degree": float(degrees.max()) if len(degrees) else 0.0,
            "min_degree": float(degrees.min()) if len(degrees) else 0.0,
            "is_directed": self.is_directed,
            "feature_dim": self.feature_dim,
        }


class ProductionGCN(nn.Module):
    """Graph convolutional network with configurable hidden layers."""

    def __init__(
        self,
        input_dim: int,
        hidden_dims: list,
        output_dim: int,
        dropout: float = 0.5,
        batch_norm: bool = True,
        activation: str = "relu",
        final_activation: str = "relu",
    ):
        super().__init__()

        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.output_dim = output_dim

        self.convs = nn.ModuleList()
        self.batch_norms = nn.ModuleList()
        self.dropouts = nn.ModuleList()

        self.convs.append(GCNConv(input_dim, hidden_dims[0]))
        if batch_norm:
            self.batch_norms.append(nn.BatchNorm1d(hidden_dims[0]))
        self.dropouts.append(nn.Dropout(dropout))

        for i in range(len(hidden_dims) - 1):
            self.convs.append(GCNConv(hidden_dims[i], hidden_dims[i + 1]))
            if batch_norm:
                self.batch_norms.append(nn.BatchNorm1d(hidden_dims[i + 1]))
            self.dropouts.append(nn.Dropout(dropout))

        self.convs.append(GCNConv(hidden_dims[-1], output_dim))

        self.activation = self._get_activation(activation)
        self.final_activation = self._get_activation(final_activation)
        self.use_batch_norm = batch_norm

    def _get_activation(self, activation: str):
        activations = {
            "relu": F.relu,
            "leaky_relu": F.leaky_relu,
            "tanh": torch.tanh,
            "sigmoid": torch.sigmoid,
            "none": lambda x: x,
        }
        return activations.get(activation.lower(), F.relu)

    def forward(self, x, edge_index):
        for i in range(len(self.convs) - 1):
            x = self.dropouts[i](x)
            x = self.convs[i](x, edge_index)
            if self.use_batch_norm and i < len(self.batch_norms):
                x = self.batch_norms[i](x)
            x = self.activation(x)

        x = self.convs[-1](x, edge_index)
        return self.final_activation(x)


class ProductionNOCD(nn.Module):
    """NOCD model (Shchur and Günnemann; 2019)."""

    def __init__(
        self,
        input_dim: int,
        num_communities: int,
        hidden_dim: int = 128,
        dropout: float = 0.5,
    ):
        super().__init__()

        self.input_dim = input_dim
        self.num_communities = num_communities
        self.hidden_dim = hidden_dim

        self.gcn = ProductionGCN(
            input_dim=input_dim,
            hidden_dims=[hidden_dim],
            output_dim=num_communities,
            dropout=dropout,
            batch_norm=True,
            activation="relu",
            final_activation="relu",
        )

    def normalize_features(self, x):
        return F.normalize(x, p=2, dim=1)

    def forward(self, x, edge_index):
        x = self.normalize_features(x)
        return self.gcn(x, edge_index)

    def predict_communities(self, x, edge_index, threshold: float = 0.5):
        self.eval()
        with torch.no_grad():
            affiliations = self.forward(x, edge_index)
            communities = (affiliations > threshold).float()
        return communities, affiliations


class BernoulliPoissonLoss(nn.Module):
    """Balanced Bernoulli-Poisson loss (Equation 4 in the NOCD paper)."""

    def __init__(self, batch_size: int = 5000):
        super().__init__()
        self.batch_size = batch_size

    def forward(self, affiliations, edge_index, num_nodes):
        num_edges = edge_index.shape[1]

        if num_edges > self.batch_size:
            edge_indices = torch.randperm(num_edges)[: self.batch_size]
            sampled_edges = edge_index[:, edge_indices]
        else:
            sampled_edges = edge_index

        neg_edges = self._sample_negative_edges(edge_index, num_nodes, self.batch_size)

        pos_scores = self._compute_edge_scores(affiliations, sampled_edges)
        pos_loss = -torch.mean(torch.log(1 - torch.exp(-pos_scores) + 1e-8))

        neg_scores = self._compute_edge_scores(affiliations, neg_edges)
        neg_loss = torch.mean(neg_scores)

        return pos_loss + neg_loss

    def _compute_edge_scores(self, affiliations, edges):
        src_affiliations = affiliations[edges[0]]
        dst_affiliations = affiliations[edges[1]]
        return torch.sum(src_affiliations * dst_affiliations, dim=1)

    def _sample_negative_edges(self, pos_edges, num_nodes, num_samples):
        device = pos_edges.device

        neg_edges = []
        attempts = 0
        max_attempts = num_samples * 10

        pos_edge_set = set(zip(pos_edges[0].cpu().numpy(), pos_edges[1].cpu().numpy()))

        while len(neg_edges) < num_samples and attempts < max_attempts:
            src = torch.randint(0, num_nodes, (1,)).item()
            dst = torch.randint(0, num_nodes, (1,)).item()

            if (
                src != dst
                and (src, dst) not in pos_edge_set
                and (dst, src) not in pos_edge_set
            ):
                neg_edges.append([src, dst])
            attempts += 1

        while len(neg_edges) < num_samples:
            src = torch.randint(0, num_nodes, (1,)).item()
            dst = torch.randint(0, num_nodes, (1,)).item()
            if src != dst:
                neg_edges.append([src, dst])

        return torch.tensor(neg_edges[:num_samples], device=device).t()


class NOCDTrainer:
    """Training loop for :class:`ProductionNOCD`."""

    def __init__(
        self,
        model: ProductionNOCD,
        dataset: CSRGraphDataset,
        lr: float = 1e-3,
        weight_decay: float = 1e-2,
        device: str = "auto",
        batch_size: int = 500,
    ):
        self.model = model
        self.dataset = dataset
        self.batch_size = batch_size

        if device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        self.model.to(self.device)

        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=lr,
            weight_decay=weight_decay,
        )

        self.criterion = BernoulliPoissonLoss(batch_size=batch_size)
        self.history = {"loss": [], "epoch": [], "full_loss": []}

    def train(
        self,
        epochs: int = 5000,
        patience_epochs: int = 5,
        eval_frequency: int = 50,
        checkpoint_dir: str | None = None,
    ):
        data = self.dataset.to_pyg_data().to(self.device)

        best_loss = float("inf")
        patience_counter = 0

        for epoch in range(epochs):
            self.model.train()
            self.optimizer.zero_grad()

            affiliations = self.model(data.x, data.edge_index)
            loss = self.criterion(affiliations, data.edge_index, data.num_nodes)

            loss.backward()
            self.optimizer.step()

            self.history["loss"].append(loss.item())
            self.history["epoch"].append(epoch)

            if epoch % eval_frequency == 0:
                with torch.no_grad():
                    full_criterion = BernoulliPoissonLoss(
                        batch_size=data.edge_index.shape[1]
                    )
                    full_loss = full_criterion(
                        affiliations, data.edge_index, data.num_nodes
                    ).item()
                    self.history["full_loss"].append(full_loss)

                    if full_loss < best_loss:
                        best_loss = full_loss
                        patience_counter = 0
                        if checkpoint_dir:
                            self.save_checkpoint(checkpoint_dir, epoch, is_best=True)
                    else:
                        patience_counter += 1

                    if patience_counter >= patience_epochs:
                        break

        return self.history

    def save_checkpoint(self, checkpoint_dir: str, epoch: int, is_best: bool = False):
        Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)

        checkpoint = {
            "epoch": epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "history": self.history,
            "model_config": {
                "input_dim": self.model.input_dim,
                "num_communities": self.model.num_communities,
                "hidden_dim": self.model.hidden_dim,
            },
        }

        filename = "best_model.pth" if is_best else f"checkpoint_epoch_{epoch}.pth"
        torch.save(checkpoint, Path(checkpoint_dir) / filename)

    def evaluate(self, threshold: float = 0.5):
        data = self.dataset.to_pyg_data().to(self.device)

        communities, affiliations = self.model.predict_communities(
            data.x, data.edge_index, threshold
        )

        return {
            "communities": communities.cpu().numpy(),
            "affiliations": affiliations.cpu().numpy(),
            "num_communities_per_node": communities.sum(dim=1).cpu().numpy(),
            "avg_communities_per_node": communities.sum(dim=1).float().mean().item(),
        }
