"""
File: gpu_init.py
Author: Dmitry Ryumin
Description: GPU initialization.
License: MIT License
"""

import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
