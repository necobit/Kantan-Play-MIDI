"""
データモデルの定義
"""
from dataclasses import dataclass
from typing import List


@dataclass
class Note:
    """音符データを表すクラス"""
    degree: str
    modifier1: int = 0
    modifier2: int = 0
    modifier3: int = 0

    def __post_init__(self) -> None:
        """初期化後の検証"""
        # degreeの検証
        valid_degrees = ["1", "2b", "2", "3b", "3", "4", "5b", "5", "6b", "6", "7b", "7"]
        if self.degree not in valid_degrees:
            raise ValueError(f"Invalid degree: {self.degree}. Must be one of {valid_degrees}")
        
        # modifierの検証
        for i, modifier in enumerate([self.modifier1, self.modifier2, self.modifier3], 1):
            if not 0 <= modifier <= 8:
                raise ValueError(f"modifier{i} must be between 0 and 8, got {modifier}")


@dataclass
class Performance:
    """演奏データ全体を表すクラス"""
    slot: int
    tempo: int
    notes: List[Note]

    def __post_init__(self) -> None:
        """初期化後の検証"""
        # slotの検証
        if not 1 <= self.slot <= 8:
            raise ValueError(f"slot must be between 1 and 8, got {self.slot}")
        
        # tempoの検証
        if not 20 <= self.tempo <= 600:
            raise ValueError(f"tempo must be between 20 and 600 BPM, got {self.tempo}")
        
        # notesの検証
        if not self.notes:
            raise ValueError("notes list cannot be empty")