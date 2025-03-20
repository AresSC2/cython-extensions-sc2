# distutils: language = c++

#include <functional>
#include <queue>

import numpy as np

cimport numpy as cnp
from libcpp cimport bool
from libcpp.pair cimport pair

ctypedef cnp.float64_t DTYPE_t


cdef extern from "dijkstra_priority_queue.hpp":
    cdef cppclass cpp_pq:
        cpp_pq(...) except +
        void push(pair[double,pair[int, int]])
        pair[double,pair[int, int]] top()
        void pop()
        bool empty()


cdef bool compare_element(pair[double,pair[int, int]] a, pair[double,pair[int, int]] b):
    return a.first > b.first


cdef class DijkstraOutput:
    cdef public Py_ssize_t[:, :] prev_x
    cdef public Py_ssize_t[:, :] prev_y
    cdef public DTYPE_t[:, :] dist
    def __cinit__(self,
                  Py_ssize_t[:, :] prev_x,
                  Py_ssize_t[:, :] prev_y,
                  DTYPE_t[:, :] dist,
                  ):
        self.prev_x = prev_x
        self.prev_y = prev_y
        self.dist = dist

    cpdef get_path(self,
                 (int, int) source,
                 int limit) except *:

        path = list[tuple[int, int]]()
        x, y = source
        while len(path) < limit:
            if x < 0 or y < 0:
                break
            path.append((x, y))
            x, y = self.prev_x[x, y], self.prev_y[x, y]
        return path


cpdef DijkstraOutput cy_dijkstra(
    DTYPE_t[:, :] cost,
    Py_ssize_t[:, :] targets,
):


    cdef:
        DTYPE_t _sqrt2 = np.sqrt(2)
        Py_ssize_t[8] neighbours_x = [-1, 1, 0, 0, -1, 1, -1, 1]
        Py_ssize_t[8] neighbours_y = [0, 0, -1, 1, -1, -1, 1, 1]
        DTYPE_t[8] neighbours_d = [1, 1, 1, 1, _sqrt2, _sqrt2, _sqrt2, _sqrt2]
        DTYPE_t[:, :] dist = np.full_like(cost, np.inf)
        DTYPE_t[:, :] cost_padded = np.pad(cost, 1, "constant", constant_values=np.inf)
        Py_ssize_t[:, :] prev_x = np.full_like(cost, -1, np.intp)
        Py_ssize_t[:, :] prev_y = np.full_like(cost, -1, np.intp)
        cpp_pq q = cpp_pq(compare_element)
        Py_ssize_t x, y, x2, y2
        DTYPE_t alternative
        pair[double, pair[int, int]] u, v

    if np.any(np.less_equal(cost, 0.0)):
        raise Exception("invalid cost: entries must be strictly positive")

    if (
        np.less(targets, 0).any()
        or np.greater_equal(targets[:, 0], cost.shape[0]).any()
        or np.greater_equal(targets[:, 1], cost.shape[1]).any()
    ):
        raise Exception("Target out of bounds")

    for i in range(targets.shape[0]):
        x = targets[i, 0]
        y = targets[i, 1]
        c = cost[x, y]
        u = (c, (x, y))
        q.push(u)
        dist[x, y] = c

    while not q.empty():
        u = q.top()
        q.pop()
        x = u.second.first
        y = u.second.second
        for k in range(8):
            x2 = x + neighbours_x[k]
            y2 = y + neighbours_y[k]
            if x2 < 0 or cost.shape[0] <= x2:
                continue
            if y2 < 0 or cost.shape[1] <= y2:
                continue
            alternative = dist[x, y] + neighbours_d[k] * cost_padded[x2+1, y2+1]
            if alternative < dist[x2, y2]:
                dist[x2, y2] = alternative
                prev_x[x2, y2] = x
                prev_y[x2, y2] = y
                v = (alternative, (x2, y2))
                q.push(v)

    return DijkstraOutput(prev_x, prev_y, dist)