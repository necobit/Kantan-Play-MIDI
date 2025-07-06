"""
MIDI演奏制御モジュール（プレースホルダー）
"""
from typing import List, Optional
import time


class MIDIPlayer:
    """MIDI演奏を制御するクラス"""

    def __init__(self, midi_port: Optional[str] = None):
        """
        Args:
            midi_port: 使用するMIDIポート名
        """
        self.midi_port = midi_port
        self.channel = 0  # チャンネル1 (0-indexed)

    def connect(self) -> None:
        """MIDIポートに接続する"""
        # TODO: 実装予定
        pass

    def disconnect(self) -> None:
        """MIDIポートから切断する"""
        # TODO: 実装予定
        pass

    def send_note_on(self, note: int, velocity: int = 127) -> None:
        """
        ノートオンメッセージを送信
        
        Args:
            note: MIDIノートナンバー
            velocity: ベロシティ (0-127)
        """
        # TODO: 実装予定
        pass

    def send_note_off(self, note: int) -> None:
        """
        ノートオフメッセージを送信
        
        Args:
            note: MIDIノートナンバー
        """
        # TODO: 実装予定
        pass

    def press_button(self, note: int, duration_ms: int = 50) -> None:
        """
        ボタン押下をシミュレート（ノートオン→待機→ノートオフ）
        
        Args:
            note: MIDIノートナンバー
            duration_ms: 押下時間（ミリ秒）
        """
        self.send_note_on(note)
        time.sleep(duration_ms / 1000.0)
        self.send_note_off(note)