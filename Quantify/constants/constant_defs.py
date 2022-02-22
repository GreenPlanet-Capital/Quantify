import os
import Quantify
import inspect
tracked_trades_path = os.path.join(
    os.path.dirname(inspect.getfile(Quantify)), 
    'data', 'tracked_files'
)
untracked_trades_path = os.path.join(
    os.path.dirname(inspect.getfile(Quantify)), 
    'data', 'untracked_files'
)