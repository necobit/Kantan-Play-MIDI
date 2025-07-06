"""
MIDI設定管理モジュール
"""
import json
from pathlib import Path
from typing import Dict, List


class MIDIConfig:
    """MIDI.jsonファイルの設定を管理するクラス"""

    def __init__(self, config_path: Path):
        """
        Args:
            config_path: MIDI.jsonファイルのパス
        """
        self.config_path = config_path
        self._config: Dict[str, List[int]] = {}
        self.load()

    def load(self) -> None:
        """設定ファイルを読み込む"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = json.load(f)

    @property
    def slot_notes(self) -> List[int]:
        """スロット用のMIDIノートナンバーリストを返す"""
        return self._config.get('slot', [])

    @property
    def degree_notes(self) -> List[int]:
        """音階用のMIDIノートナンバーリストを返す"""
        return self._config.get('notes', [])

    @property
    def modifier1_notes(self) -> List[int]:
        """modifier1用のMIDIノートナンバーリストを返す"""
        return self._config.get('modifier1', [])

    @property
    def modifier2_notes(self) -> List[int]:
        """modifier2用のMIDIノートナンバーリストを返す"""
        return self._config.get('modifier2', [])

    @property
    def modifier3_notes(self) -> List[int]:
        """modifier3用のMIDIノートナンバーリストを返す"""
        return self._config.get('modifier3', [])