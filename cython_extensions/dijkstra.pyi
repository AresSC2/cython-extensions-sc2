import numpy as np


class DijkstraOutput:
    """Result of Dijkstras algorithm containing distance and forward pointer grids.

    """
    forward_x: np.ndarray
    """Forward pointer grid (x-coordinates)."""
    forward_y: np.ndarray
    """Forward pointer grid (y-coordinates)."""
    distance: np.ndarray
    """Distance grid."""

    def get_path(self, source: tuple[int, int], limit: int = 0) -> list[tuple[int, int]]:
        """Follow the path from a given source using the forward pointer grids.

        Args:
            source: Start point.
            limit: Maximum length of the returned path. Defaults to 0 indicating no limit.

        Returns:
            The lowest cost path from source to any of the targets.
            
        """
        ...


def cy_dijkstra(cost_grid: np.ndarray, targets: np.ndarray, checks_enabled: bool = True) -> DijkstraOutput:
    """Run Dijkstras algorithm on a grid, yielding many-target-shortest paths for each position.
    
    Args:
        cost_grid: Cost grid. Entries must be positive. Set unpathable cells to infinity.
        targets: Target array of shape (*, 2) containing x and y coordinates of the target points.
        checks_enabled: Pass False to deactivate grid value and target coordinates checks. Defaults to True.
        
    Returns:
        Pathfinding object containing distances and pointer grids.
        
    """
    ...