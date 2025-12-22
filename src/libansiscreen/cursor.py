# libansiscreen/cursor.py

from dataclasses import dataclass


@dataclass(slots=True)
class Cursor:
    """
    Cursor stores position state only.

    All bounds checking, wrapping, scrolling, and semantics
    are handled by Screen.
    """
    x: int = 0
    y: int = 0

    _saved_x: int = 0
    _saved_y: int = 0

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def set(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def move(self, dx: int = 0, dy: int = 0) -> None:
        self.x += dx
        self.y += dy

    # ------------------------------------------------------------------
    # Save / restore (ANSI DECSC / DECRC, CSI s / CSI u)
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Save current cursor position."""
        self._saved_x = self.x
        self._saved_y = self.y

    def restore(self) -> None:
        """Restore previously saved cursor position."""
        self.x = self._saved_x
        self.y = self._saved_y

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """
        Reset cursor to origin and clear saved position.
        """
        self.x = 0
        self.y = 0
        self._saved_x = 0
        self._saved_y = 0
