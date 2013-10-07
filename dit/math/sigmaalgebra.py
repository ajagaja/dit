"""
    Functions for generating sigma algebras on finite sets.

    Chetan Jhurani
    http://users.ices.utexas.edu/~chetan/Publications.html
    http://users.ices.utexas.edu/~chetan/reports/2009-03-ices-set_algebra_algorithms.pdf

"""

from collections import defaultdict

import numpy as np

from dit.utils import powerset

__all__ = ['is_sigma_algebra', 'sigma_algebra', 'atom_set']

def sets2matrix(C, X=None):
    """Returns the sets in C as binary strings representing elements in X.

    Paramters
    ---------
    C : set of frozensets
        The set of subsets of X.
    X : frozenset, None
        The underlying set. If None, then X is taken to be the union of the
        sets in C.

    Returns
    -------
    Cmatrix : NumPy array, shape ( len(C), len(X) )
        The 0-1 matrix whose rows represent sets in C. The columns tell us
        if the corresponding element in X is present in the subset of C.
    Xset : frozenset
        The underlying set that was used to construct Cmatrix.

    """
    # make sure C consists of frozensets and that X is frozen
    C = set([frozenset(c) for c in C])
    if X is None:
        Xset = frozenset().union(*C)
    else:
        Xset = frozenset(X)
        for cet in C:
            if not Xset.issuperset(cet):
                msg = "Set {0} is not a subset of {1}".format(cet, Xset)
                raise Exception(msg)

    # Each element of C will be represented as a binary string of 0s and 1s.
    # Note, X is frozen, so its iterating order is fixed.
    Cmatrix = [[ 1 if x in cet else 0 for x in Xset ] for cet in C]
    Cmatrix = np.array(Cmatrix, dtype=int)

    return Cmatrix, Xset

def unique_columns(Cmatrix):
    """Returns a dictionary mapping columns to identical column indexes.

    Parameters
    ----------
    Cmatrix : NumPy array
        A 0-1 matrix whose rows represent subsets of an underlying set. The
        columns express membership of the underlying set's elements in
        each of the subsets.

    Returns
    -------
    unique_cols : defaultdict(set)
        A dictionary mapping columns in Cmatrix to sets of column indexes.
        All indexes that mapped from the same set represent identical columns.

    """
    unique_cols = defaultdict(set)
    for idx, col in enumerate(Cmatrix.transpose()):
        unique_cols[tuple(col)].add(idx)
    return unique_cols

def sigma_algebra(C, X=None):
    """Returns the sigma algebra generated by the subsets in C.

    Let X be a set and C be a collection of subsets of X.  The sigma algebra
    generated by the subsets in C is the smallest sigma-algebra which contains
    every subset in C.

    Parameters
    ----------
    C : set of frozensets
        The set of subsets of X.
    X : frozenset, None
        The underlying set. If None, then X is taken to be the union of the
        sets in C.

    Returns
    -------
    sC : frozenset of frozensets
        The sigma-algebra generated by C.

    Notes
    -----
    The algorithm run time is generally exponential in |X|, the size of X.

    """
    from itertools import product

    Cmatrix, X = sets2matrix(C, X)
    unique_cols = unique_columns(Cmatrix)

    # Create a lookup from column IDs representing identical columns to the
    # index of a unique representative in the list of unique representatives.
    # This will be used to repopulate the larger binary string representation.
    lookups = {}
    for i, indexes in enumerate(unique_cols.values()):
        for index in indexes:
            lookups[index] = i

    # The total number of elements is given by the powerset on all unique
    # indexes. That is, we just generate all binary strings. Then, for each
    # binary string, we construct the subset in the sigma algebra.
    sC = set([])
    for word in product([0,1], repeat=len(unique_cols)):
        subset = [x for i,x in enumerate(X) if word[lookups[i]] == 1]
        sC.add( frozenset(subset) )
    sC = frozenset(sC)

    return sC

def is_sigma_algebra(F, X=None):
    """Returns True if F is a sigma algebra on X.

    Parameters
    ----------
    F : set of frozensets
        The candidate sigma algebra.
    X : frozenset, None
        The universal set. If None, then X is taken to be the union of the
        sets in F.

    Returns
    -------
    issa : bool
        True if F is a sigma algebra and False if not.

    Notes
    -----
    The time complexity of this algorithm is O ( len(F) * len(X) ).

    """
    # The idea is to construct the matrix representing F. Then count the number
    # of redundant columns. Denote this number by q. If F is a sigma algebra
    # on a finite set X, then we must have:
    #    m + 2 == 2**(len(X) - q)).
    # where m is the number of elements in F not equal to the empty set or
    # or the universal set X.

    Fmatrix, X = sets2matrix(F, X)
    unique_cols = unique_columns(Fmatrix)

    m = len(F)
    emptyset = set([])
    if emptyset in F:
        m -= 1
    if X in F:
        m -= 1

    if m + 2 == 2**len(unique_cols):
        return True
    else:
        return False

def is_sigma_algebra__brute(F, X=None):
    """Returns True if F is a sigma algebra on X.

    Parameters
    ----------
    F : set of frozensets
        The candidate sigma algebra.
    X : frozenset, None
        The universal set. If None, then X is taken to be the union of the
        sets in F.

    Returns
    -------
    issa : bool
        True if F is a sigma algebra and False if not.

    Notes
    -----
    This is a brute force check against the definition of a sigma algebra
    on a finite set. Its time complexity is O( len(F)**2 ).

    """
    # This works because its not necessary to test countable unions if the
    # base set X is finite.  One need only consider pairwise unions.
    if X is None:
        X = frozenset().union(*F)
    else:
        X = frozenset(X)

    for subset1 in F:
        if X.difference(subset1) not in F:
            return False
        for subset2 in F:
            if subset1.union(subset2) not in F:
                return False
    else:
        return True

def atom_set(F, X=None):
    """
    Returns the atoms of the sigma-algebra F.

    Parameters
    ----------
    F : set of frozensets
        The candidate sigma algebra.
    X : frozenset, None
        The universal set. If None, then X is taken to be the union of the
        sets in F.

    Returns
    -------
    atoms : frozenset
        A frozenset of frozensets, representing the atoms of the sigma algebra.

    """
    if not isinstance(next(iter(F)), frozenset):
        raise Exception('Input to `atom_set` must contain frozensets.')

    atoms = []
    for cet in F:
        if not cet:
            # An atom must be nonempty.
            continue

        # Now look at all nonempty, proper subsets of cet.
        subsets = list(powerset(cet))[1:-1]
        for subset in subsets:
            if frozenset(subset) in F:
                break
        else:
            # Then `cet` has no proper subset that is also in F.
            atoms.append(frozenset(cet))

    return frozenset(atoms)
