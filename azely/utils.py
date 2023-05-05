"""Azely's utils module (low-level utilities).

This module provides series of utility related to exception and I/O:
(1) ``AzelyError`` class as Azely's base exception class

"""
__all__ = ["AzelyError"]


class AzelyError(Exception):
    """Azely's base exception class."""

    pass
