"""Reproducibility helpers."""

from __future__ import annotations

import os
import random

import numpy as np

try:
    import torch
except ImportError:  # pragma: no cover - torch is optional for the current slice
    torch = None


def set_global_seed(seed: int = 42) -> None:
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)

    if torch is None:
        return

    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def worker_init_fn(worker_id: int) -> None:
    base_seed = int(os.environ.get("PYTHONHASHSEED", "42"))
    seed = (base_seed + worker_id) % (2**32)
    np.random.seed(seed)
    random.seed(seed)
