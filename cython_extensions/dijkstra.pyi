import numpy as np


class DijkstraOutput:
    """Result of Dijkstras algorithm containing distance and predecessor pointers per cell.

    """
    prev_x: np.ndarray
    prev_y: np.ndarray
    dist: np.ndarray

    def get_path(self, source: tuple[int, int], limit: int) -> list[tuple[int, int]]:
        """Follow the path from a given source using the precalculated pointer arrays.
        
        Parameters
        ----------
        source :
            The start point of the path.
        limit :
            Maximum returned path length. Reduce for a small speedup.
            
        Returns
        -------
        list[tuple[int, int]] :
            The lowest cost path from source to any of the targets.
            
        """
        ...


def cy_dijkstra(cost: np.ndarray, targets: np.ndarray) -> DijkstraOutput:
    """Run Dijkstras algorithm on a grid, precalulating paths from all points to one of the targets.
    
    Parameters
    ----------
    cost :
        Cost array of shape (n, m). Entries must be positive. Use infinity to mark unpathable cells.
    targets :
        Target array of shape (k, 2) containing x and y coordinates of the target points.
        
    Returns
    -------
    DijkstraOutput :
        Pathfinding object containing pointer arrays used to construct paths.
        
    """
    ...