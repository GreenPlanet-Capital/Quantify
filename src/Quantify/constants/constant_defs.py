import os
import Quantify
import inspect

tracked_trades_path = os.path.join(
    os.path.dirname(inspect.getfile(Quantify)), "data", "tracked_files"
)
os.makedirs(tracked_trades_path, exist_ok=True)
untracked_trades_path = os.path.join(
    os.path.dirname(inspect.getfile(Quantify)), "data", "untracked_files"
)
os.makedirs(untracked_trades_path, exist_ok=True)
