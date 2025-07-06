"""
演奏シーケンス管理モジュール
"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class MIDIEventType(Enum):
    """MIDIイベントの種類"""
    NOTE_ON = "note_on"
    NOTE_OFF = "note_off"
    SLOT_PRESS = "slot_press"


@dataclass
class MIDIEvent:
    """個別のMIDIイベント"""
    timestamp: float  # 秒単位の絶対時刻
    event_type: MIDIEventType
    note: int  # MIDIノートナンバー
    velocity: int = 127
    duration: Optional[float] = None  # イベントの継続時間（秒）
    description: str = ""  # デバッグ用の説明


@dataclass
class PlaybackSequence:
    """演奏シーケンス全体"""
    events: List[MIDIEvent]
    total_duration: float  # 全体の演奏時間（秒）
    slot: int
    tempo: int

    def get_events_at_time(self, timestamp: float, tolerance: float = 0.001) -> List[MIDIEvent]:
        """指定時刻のイベントを取得"""
        return [
            event for event in self.events
            if abs(event.timestamp - timestamp) <= tolerance
        ]

    def get_events_in_range(self, start_time: float, end_time: float) -> List[MIDIEvent]:
        """指定時間範囲のイベントを取得"""
        return [
            event for event in self.events
            if start_time <= event.timestamp <= end_time
        ]

    def sort_events(self) -> None:
        """イベントを時刻順にソート"""
        self.events.sort(key=lambda event: (event.timestamp, event.event_type.value))