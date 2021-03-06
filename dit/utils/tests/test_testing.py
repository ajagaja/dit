"""
Tests for dit.util.testing
"""

import pytest

from hypothesis import find

from dit.multivariate import coinformation
from dit.utils.testing import distributions

@pytest.mark.flaky(reruns=5)
def test_distributions1():
    """
    A test for the distributions strategy.
    """
    example = find(distributions(3, 2), lambda d: coinformation(d) < -0.5)
    assert coinformation(example) <= -0.5

@pytest.mark.flaky(reruns=5)
def test_distributions2():
    """
    A test for the distributions strategy.
    """
    example = find(distributions(3, 2, uniform=True), lambda d: coinformation(d) < -0.5)
    assert coinformation(example) <= -0.5
