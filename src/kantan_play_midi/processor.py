"""
パフォーマンス処理モジュール
"""
from typing import List

from .models import Performance, Note
from .config import MIDIConfig
from .converter import MIDIConverter
from .timing import TimingCalculator
from .sequence import PlaybackSequence, MIDIEvent, MIDIEventType


class PerformanceProcessor:
    """演奏データを処理してMIDIシーケンスを生成するクラス"""

    def __init__(self, config: MIDIConfig):
        """
        Args:
            config: MIDI設定オブジェクト
        """
        self.config = config
        self.converter = MIDIConverter(config)

    def process_performance(self, performance: Performance) -> PlaybackSequence:
        """
        演奏データを処理してMIDIシーケンスを生成
        
        Args:
            performance: 演奏データ
            
        Returns:
            PlaybackSequence: 再生シーケンス
        """
        timing_calc = TimingCalculator(performance.tempo)
        events: List[MIDIEvent] = []

        # 1. スロット選択イベント
        slot_event = self._create_slot_event(performance.slot, timing_calc)
        events.append(slot_event)

        # 2. 各音符の処理
        note_timings = timing_calc.calculate_note_timings(len(performance.notes))
        
        for i, note in enumerate(performance.notes):
            note_start_time = note_timings[i]
            note_events = self._process_note(note, note_start_time, timing_calc, i + 1)
            events.extend(note_events)

        # 3. 演奏時間の計算
        total_duration = timing_calc.get_total_duration(len(performance.notes))

        # 4. シーケンスの作成とソート
        sequence = PlaybackSequence(
            events=events,
            total_duration=total_duration,
            slot=performance.slot,
            tempo=performance.tempo
        )
        sequence.sort_events()

        return sequence

    def _create_slot_event(self, slot: int, timing_calc: TimingCalculator) -> MIDIEvent:
        """スロット選択イベントを作成"""
        slot_note = self.converter.convert_slot(slot)
        if slot_note is None:
            raise ValueError(f"Invalid slot: {slot}")

        return MIDIEvent(
            timestamp=timing_calc.calculate_slot_timing(),
            event_type=MIDIEventType.SLOT_PRESS,
            note=slot_note,
            duration=0.05,  # 50ms
            description=f"Slot {slot} selection"
        )

    def _process_note(
        self, 
        note: Note, 
        note_start_time: float, 
        timing_calc: TimingCalculator,
        note_index: int
    ) -> List[MIDIEvent]:
        """1つの音符を処理してMIDIイベントリストを生成"""
        events: List[MIDIEvent] = []

        # 1. モディファイアの処理
        modifier_notes = self._get_active_modifiers(note)
        modifier_start_time = timing_calc.calculate_modifier_timing(note_start_time)
        modifier_end_time = timing_calc.calculate_modifier_release_timing(note_start_time)

        # モディファイア押下
        for mod_num, mod_note in modifier_notes:
            events.append(MIDIEvent(
                timestamp=modifier_start_time,
                event_type=MIDIEventType.NOTE_ON,
                note=mod_note,
                description=f"Note {note_index}: Modifier{mod_num} press"
            ))

        # 2. degree ボタンの8回押下
        degree_note = self.converter.convert_degree(note.degree)
        if degree_note is None:
            raise ValueError(f"Invalid degree: {note.degree}")

        degree_timings = timing_calc.calculate_degree_press_timings(note_start_time)
        for i, press_time in enumerate(degree_timings, 1):
            # ノートオン
            events.append(MIDIEvent(
                timestamp=press_time,
                event_type=MIDIEventType.NOTE_ON,
                note=degree_note,
                description=f"Note {note_index}: Degree '{note.degree}' press {i}/8"
            ))
            
            # ノートオフ（短い間隔で）
            events.append(MIDIEvent(
                timestamp=press_time + 0.05,  # 50ms後
                event_type=MIDIEventType.NOTE_OFF,
                note=degree_note,
                description=f"Note {note_index}: Degree '{note.degree}' release {i}/8"
            ))

        # 3. モディファイア解放
        for mod_num, mod_note in modifier_notes:
            events.append(MIDIEvent(
                timestamp=modifier_end_time,
                event_type=MIDIEventType.NOTE_OFF,
                note=mod_note,
                description=f"Note {note_index}: Modifier{mod_num} release"
            ))

        return events

    def _get_active_modifiers(self, note: Note) -> List[tuple]:
        """アクティブなモディファイアのMIDIノート番号を取得"""
        modifiers = []
        
        for mod_num in [1, 2, 3]:
            mod_value = getattr(note, f"modifier{mod_num}")
            if mod_value > 0:
                mod_note = self.converter.convert_modifier(mod_num, mod_value)
                if mod_note is not None:
                    modifiers.append((mod_num, mod_note))
        
        return modifiers

    def get_sequence_summary(self, sequence: PlaybackSequence) -> str:
        """シーケンスの概要を文字列で取得"""
        summary_lines = [
            f"演奏シーケンス概要:",
            f"  スロット: {sequence.slot}",
            f"  テンポ: {sequence.tempo} BPM",
            f"  総演奏時間: {sequence.total_duration:.2f}秒",
            f"  総イベント数: {len(sequence.events)}",
            "",
            "イベント内訳:"
        ]

        # イベントタイプ別の集計
        event_counts = {}
        for event in sequence.events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        for event_type, count in event_counts.items():
            summary_lines.append(f"  {event_type}: {count}回")

        return "\n".join(summary_lines)