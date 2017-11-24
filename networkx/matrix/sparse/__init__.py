# -*- coding: utf-8 -*-


"""
=====================
Sparse Matrix Modules
=====================

:Author:
    Moritz E. Beber <moritz.beber@gmail.com>
:Date:
    2014-03-18
:Copyright:
    See LICENSE.rst and the LICENSES folder for detailed information.
    Copyright |c| 2014, Moritz E. Beber, all rights reserved.
:File:
    __init__.py

.. |c| unicode:: U+A9
"""


from .algorithms import *
from .classes import *
from .generators import *


SCIPY_FORMATS = {
    "bsr": sp.bsr_matrix,
    "coo": sp.coo_matrix,
    "csc": sp.csc_matrix,
    "csr": sp.csr_matrix,
    "dia": sp.dia_matrix,
    "dok": sp.dok_matrix,
    "lil": sp.lil_matrix
    }

