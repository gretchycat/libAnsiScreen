from __future__ import annotations

from typing import Optional, Tuple

from libansiscreen.screen import Screen
from libansiscreen.ops.copy import copy
from libansiscreen.ops.clear import clear


Box = Tuple[int, int, int, int]


def cut(screen: Screen, box: Optional[Box] = None) -> Screen:
    """
    Cut a region from a screen: copy it, then clear the original region.

    If box is None, cuts the entire screen.
    """
    buf = copy(screen, box)
    clear(screen, box)
    return buf
