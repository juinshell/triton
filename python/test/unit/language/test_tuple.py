import pytest
import triton
import triton.language as tl
import torch


@triton.jit
def _tuple_increment(values):
    for i in tl.static_range(len(values)):
        values[i] = values[i] + 1
    return values


@triton.jit
def _tuple_index_func(Ptrs, values):
    for i in tl.static_range(len(values)):
        tl.store(Ptrs[i], values[i])


@triton.jit
def _tuple_index(_0, Ptrs, _1: tl.constexpr, values, _2, _3: tl.constexpr, _4):
    values = _tuple_increment(values)
    _tuple_index_func(Ptrs, values)


@pytest.mark.parametrize("size", [0, 1, 2, 3, 4])
def test_index(size, device="cuda"):
    vals = tuple([i + 1 for i in range(size)])
    rets = tuple([torch.zeros((1, ), dtype=torch.float32, device=device) for _ in vals])
    _tuple_index[(1, )](0, rets, 0, vals, 0, 0, 0)
    assert vals == tuple([x.item() - 1 for x in rets])


# ----


@triton.jit
def _tuple_assign(XPtrs, YPtrs, values):
    # assign from tuple
    X0, X1 = XPtrs
    x0, x1 = values
    tl.store(X0, x0)
    tl.store(X1, x1)
    # assign to tuple
    Y0, Y1, Y2 = YPtrs
    Y = Y0, Y1, Y2
    y = x0, 10, x1
    tl.store(Y[0], y[0])
    tl.store(Y[1], y[1])
    tl.store(Y[2], y[2])


def test_assign(device="cuda"):
    vals = (2., 3.)
    x = tuple([torch.zeros((1, ), dtype=torch.float32, device=device) for _ in range(2)])
    y = tuple([torch.zeros((1, ), dtype=torch.float32, device=device) for _ in range(3)])
    _tuple_assign[(1, )](x, y, vals)
    assert x[0] == vals[0]
    assert x[1] == vals[1]
    assert y[0] == vals[0]
    assert y[1] == 10
    assert y[2] == vals[1]


# function call (tuple argument)
# function call (tuple return value)
# __getitem__ and __setitem__
# assignment (into a tuple, from a tuple)