"""Explicit local demo reset; fixture files and legacy database are untouched."""
from .main import resolution_store
if __name__ == '__main__':
    resolution_store.reset()
    print('Resolution decisions reset. Original source mentions are separate.')
