import dataclasses
from typing import Tuple


@dataclasses.dataclass
class TextClassificationConfig:
    text_clases: Tuple[str, ...]
