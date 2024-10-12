import sys
import os

# Get the absolute path of the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Append the parent directory to sys.path
sys.path.insert(0, parent_dir)