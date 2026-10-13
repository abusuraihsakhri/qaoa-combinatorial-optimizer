import math
import pytest
from qaoa_optimizer.maxcut import validate_graph, cut_values, probabilities, optimize_maxcut

TRIANGLE = [[0, 1, 1], [1, 2, 1], [0, 2, 1]]


def test_known_triangle_optimum_and_bit_order():
    costs = cut_values(3, TRIANGLE)
    assert costs == [0, 2, 2, 2, 2, 2, 2, 0]
    result = optimize_maxcut(3, TRIANGLE)
    assert result["exact_optimum"] == 2
    assert 1 <= result["expected_cut"] <= 2 + 1e-9
    assert 0.5 <= result["approximation_ratio"] <= 1 + 1e-9
    assert len(result["distribution"]) == 8
    assert abs(sum(p["probability"] for p in result["distribution"]) - 1) < 1e-10


def test_uniform_at_zero_angles():
    p = probabilities(cut_values(3, TRIANGLE), [0.0], [0.0])
    assert all(math.isclose(x, 1 / 8) for x in p)


def test_two_layer_does_not_underperform_one_layer():
    edges = [[0,1,1],[1,2,1],[2,3,1],[3,0,1]]
    single = optimize_maxcut(4, edges, layers=1, grid=8)
    double = optimize_maxcut(4, edges, layers=2, grid=8)
    assert double["expected_cut"] >= single["expected_cut"] - 1e-9
    assert double["exact_optimum"] == 4


@pytest.mark.parametrize("vertices,edges", [
    (1, TRIANGLE), (10, TRIANGLE), (3, []), (3, [[0, 0, 1]]),
    (3, [[0, 3, 1]]), (3, [[0, 1, -1]]), (3, [[0, 1, float("nan")]]),
    (3, [[0,1,1],[1,0,2]]), (3, [[0.1,1,1]]), (3, [[0, 1, 1, 2]]),
])
def test_invalid_graph_rejected(vertices, edges):
    with pytest.raises(ValueError):
        validate_graph(vertices, edges)


def test_invalid_parameters_rejected():
    with pytest.raises(ValueError):
        optimize_maxcut(3, TRIANGLE, layers=4)
    with pytest.raises(ValueError):
        optimize_maxcut(3, TRIANGLE, grid=0)
    with pytest.raises(ValueError):
        probabilities(cut_values(3, TRIANGLE), [float("inf")], [0])
