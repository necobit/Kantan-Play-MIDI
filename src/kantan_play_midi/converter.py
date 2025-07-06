"""
JSON入力をMIDIノートナンバーに変換するモジュール
"""
from typing import Dict, List, Optional
from .config import MIDIConfig


class MIDIConverter:
    """JSON入力データをMIDIノートナンバーに変換するクラス"""

    DEGREE_MAP = {
        "1": 0, "2b": 1, "2": 2, "3b": 3, "3": 4,
        "4": 5, "5b": 6, "5": 7, "6b": 8, "6": 9,
        "7b": 10, "7": 11
    }

    def __init__(self, config: MIDIConfig):
        """
        Args:
            config: MIDI設定オブジェクト
        """
        self.config = config

    def convert_slot(self, slot: int) -> Optional[int]:
        """
        スロット番号をMIDIノートナンバーに変換
        
        Args:
            slot: スロット番号 (1-8)
            
        Returns:
            MIDIノートナンバー、無効な場合はNone
        """
        if 1 <= slot <= 8:
            return self.config.slot_notes[slot - 1]
        return None

    def convert_degree(self, degree: str) -> Optional[int]:
        """
        音階をMIDIノートナンバーに変換
        
        Args:
            degree: 音階 (例: "1", "3b", "5")
            
        Returns:
            MIDIノートナンバー、無効な場合はNone
        """
        if degree in self.DEGREE_MAP:
            index = self.DEGREE_MAP[degree]
            if index < len(self.config.degree_notes):
                return self.config.degree_notes[index]
        return None

    def convert_modifier(self, modifier_num: int, value: int) -> Optional[int]:
        """
        モディファイアをMIDIノートナンバーに変換
        
        Args:
            modifier_num: モディファイア番号 (1-3)
            value: モディファイア値 (0-8、0は無効)
            
        Returns:
            MIDIノートナンバー、無効な場合はNone
        """
        if value == 0:
            return None
            
        if 1 <= value <= 8:
            if modifier_num == 1:
                return self.config.modifier1_notes[value - 1]
            elif modifier_num == 2:
                return self.config.modifier2_notes[value - 1]
            elif modifier_num == 3:
                return self.config.modifier3_notes[value - 1]
        return None