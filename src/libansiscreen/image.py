from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ImageEntry:
    """
    Represents an image registered in the screen's image registry.
    """

    image_id: int
    image: Any  # PIL Image instance or raw image data
    width_cells: int = 1
    height_cells: int = 1
    metadata: Optional[Dict[str, Any]] = None


class ImageRegistry:
    """
    Manages image handles for Kitty, Sixel, and iTerm2 terminal graphics.
    """

    def __init__(self) -> None:
        self._next_id: int = 1
        self._images: Dict[int, ImageEntry] = {}

    def register(
        self, image: Any, width_cells: int = 1, height_cells: int = 1, metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Registers an image object and returns its unique integer image ID.
        """
        img_id = self._next_id
        self._next_id += 1
        entry = ImageEntry(
            image_id=img_id,
            image=image,
            width_cells=width_cells,
            height_cells=height_cells,
            metadata=metadata,
        )
        self._images[img_id] = entry
        return img_id

    def get(self, image_id: int) -> Optional[ImageEntry]:
        """
        Retrieves the ImageEntry for a given image ID.
        """
        return self._images.get(image_id)

    def remove(self, image_id: int) -> bool:
        """
        Removes an image from the registry.
        """
        return self._images.pop(image_id, None) is not None

    def clear(self) -> None:
        """
        Clears all registered images.
        """
        self._images.clear()
        self._next_id = 1
