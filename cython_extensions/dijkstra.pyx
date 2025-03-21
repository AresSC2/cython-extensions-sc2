# distutils: language = c++

from cython import boundscheck, wraparound
import numpy as np

from libcpp cimport bool
from libcpp.pair cimport pair

ctypedef pair[double, pair[int, int]] Item

cdef Py_ssize_t[8] NEIGHBOURS_X = [-1, 1, 0, 0, -1, 1, -1, 1]
cdef Py_ssize_t[8] NEIGHBOURS_Y = [0, 0, -1, 1, -1, -1, 1, 1]
cdef double SQRT2 = np.sqrt(2)
cdef double[8] NEIGHBOURS_D = [1, 1, 1, 1, SQRT2, SQRT2, SQRT2, SQRT2]


cdef extern from "dijkstra_priority_queue.hpp":
    cdef cppclass cpp_pq:
        cpp_pq(...) except +
        void push(Item)
        Item top()
        void pop()
        bool empty()


cdef bool compare_element(Item a, Item b):
    return a.first > b.first


cdef class DijkstraOutput:
    cdef public Py_ssize_t[:, :] forward_x
    """Forward pointer grid (x-coordinates)."""
    cdef public Py_ssize_t[:, :] forward_y
    """Forward pointer grid (y-coordinates)."""
    cdef public double[:, :] distance
    """Distance grid."""
    def __cinit__(self,
                  Py_ssize_t[:, :] forward_x,
                  Py_ssize_t[:, :] forward_y,
                  double[:, :] distance):
        self.forward_x = forward_x
        self.forward_y = forward_y
        self.distance = distance

    @boundscheck(False)
    @wraparound(False)
    cpdef get_path(self, (int, int) source, int limit=0):
        """
        
        Follow the path from a given source using the forward pointer grids.
        
        Parameters
        ----------
        source :
            Start point.
        limit :
            Maximum length of the returned path. Defaults to 0 indicating no limit.
            
        Returns
        -------
        list[tuple[int, int]] :
            The lowest cost path from source to any of the targets.
            
        """
        path = list[tuple[int, int]]()
        x, y = source
        if limit == 0:
            # set a fallback limit to be safe
            # a path longer than this must contain a cycle, so it should never be hit anyway
            limit = self.distance.shape[0] * self.distance.shape[1]

        while len(path) < limit:
            if x < 0 or y < 0:
                break
            path.append((x, y))
            x, y = self.forward_x[x, y], self.forward_y[x, y]
        return path


@boundscheck(False)
@wraparound(False)
cpdef DijkstraOutput cy_dijkstra(
    double[:, :] cost,
    Py_ssize_t[:, :] targets,
    bool checks_enabled = True,
):
    """
    
    Run Dijkstras algorithm on a grid, yielding many-target-shortest paths for each position.
    
    Parameters
    ----------
    cost :
        Cost grid. Entries must be positive. Use infinity to mark unpathable cells.
    targets :
        Target array of shape (*, 2) containing x and y coordinates of the target points.
    checks_enabled :
        Pass False to deactivate grid value and target coordinates checks. Defaults to True.
        
    Returns
    -------
    DijkstraOutput :
        Pathfinding object containing containing distance and forward pointer grids.
        
    """

    cdef:
        cpp_pq q = cpp_pq(compare_element)
        Item u
        Py_ssize_t x, y, x2, y2
        double alternative
        double[:, :] cost_padded = np.pad(cost, 1, "constant", constant_values=np.inf)
        double[:, :] distance = np.full_like(cost, np.inf)
        Py_ssize_t[:, :] forward_x = np.full_like(cost, -1, np.intp)
        Py_ssize_t[:, :] forward_y = np.full_like(cost, -1, np.intp)

    if checks_enabled:
        if np.any(np.less_equal(cost, 0.0)):
            raise Exception("invalid cost: entries must be strictly positive")

        if any((
            np.less(targets, 0).any(),
            np.greater_equal(targets[:, 0], cost.shape[0]).any(),
            np.greater_equal(targets[:, 1], cost.shape[1]).any(),
        )):
            raise Exception(f"Target out of bounds")

    # initialize queue with targets
    for i in range(targets.shape[0]):
        x = targets[i, 0]
        y = targets[i, 1]
        c = cost[x, y]
        u = (c, (x, y))
        q.push(u)
        distance[x, y] = c

    while not q.empty():
        u = q.top()
        q.pop()
        x = u.second.first
        y = u.second.second
        for k in range(8):
            x2 = x + NEIGHBOURS_X[k]
            y2 = y + NEIGHBOURS_Y[k]
            alternative = distance[x, y] + NEIGHBOURS_D[k] * cost_padded[x2+1, y2+1]
            if alternative < distance[x2, y2]:
                distance[x2, y2] = alternative
                forward_x[x2, y2] = x
                forward_y[x2, y2] = y
                u = (alternative, (x2, y2))
                q.push(u)

    return DijkstraOutput(forward_x, forward_y, distance)