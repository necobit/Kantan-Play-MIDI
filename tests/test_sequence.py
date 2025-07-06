"""
シーケンスモデルのテスト
"""
import pytest

from kantan_play_midi.sequence import MIDIEvent, MIDIEventType, PlaybackSequence


class TestMIDIEvent:
    """MIDIEventクラスのテスト"""

    def test_midi_event_creation(self):
        """MIDIEventの作成"""
        event = MIDIEvent(
            timestamp=1.5,
            event_type=MIDIEventType.NOTE_ON,
            note=60,
            velocity=100,
            description="Test event"
        )
        
        assert event.timestamp == 1.5
        assert event.event_type == MIDIEventType.NOTE_ON
        assert event.note == 60
        assert event.velocity == 100
        assert event.description == "Test event"

    def test_midi_event_defaults(self):
        """MIDIEventのデフォルト値"""
        event = MIDIEvent(
            timestamp=0.0,
            event_type=MIDIEventType.NOTE_OFF,
            note=64
        )
        
        assert event.velocity == 127
        assert event.duration is None
        assert event.description == ""


class TestPlaybackSequence:
    """PlaybackSequenceクラスのテスト"""

    @pytest.fixture
    def sample_events(self):
        """サンプルイベントのリスト"""
        return [
            MIDIEvent(0.0, MIDIEventType.SLOT_PRESS, 24),
            MIDIEvent(1.0, MIDIEventType.NOTE_ON, 60),
            MIDIEvent(1.05, MIDIEventType.NOTE_OFF, 60),
            MIDIEvent(2.0, MIDIEventType.NOTE_ON, 60),
            MIDIEvent(2.05, MIDIEventType.NOTE_OFF, 60),
            MIDIEvent(3.0, MIDIEventType.NOTE_ON, 52),  # modifier
        ]

    @pytest.fixture
    def sequence(self, sample_events):
        """サンプルシーケンス"""
        return PlaybackSequence(
            events=sample_events,
            total_duration=10.0,
            slot=1,
            tempo=120
        )

    def test_sequence_creation(self, sequence, sample_events):
        """シーケンスの作成"""
        assert sequence.total_duration == 10.0
        assert sequence.slot == 1
        assert sequence.tempo == 120
        assert len(sequence.events) == len(sample_events)

    def test_get_events_at_time(self, sequence):
        """指定時刻のイベント取得"""
        events_at_1 = sequence.get_events_at_time(1.0)
        assert len(events_at_1) == 1
        assert events_at_1[0].event_type == MIDIEventType.NOTE_ON

        events_at_0 = sequence.get_events_at_time(0.0)
        assert len(events_at_0) == 1
        assert events_at_0[0].event_type == MIDIEventType.SLOT_PRESS

        # 存在しない時刻
        events_at_5 = sequence.get_events_at_time(5.0)
        assert len(events_at_5) == 0

    def test_get_events_at_time_with_tolerance(self, sequence):
        """許容誤差付きでの指定時刻イベント取得"""
        # 1.001秒での検索（1.0秒のイベントが見つかる）
        events = sequence.get_events_at_time(1.001, tolerance=0.01)
        assert len(events) == 1

        # 許容誤差を狭めた場合
        events = sequence.get_events_at_time(1.001, tolerance=0.0001)
        assert len(events) == 0

    def test_get_events_in_range(self, sequence):
        """時間範囲でのイベント取得"""
        events_0_to_2 = sequence.get_events_in_range(0.0, 2.0)
        assert len(events_0_to_2) == 4  # 0.0, 1.0, 1.05, 2.0のイベント

        events_1_to_3 = sequence.get_events_in_range(1.0, 3.0)
        assert len(events_1_to_3) == 5  # 1.0, 1.05, 2.0, 2.05, 3.0のイベント

        # 範囲外
        events_10_to_20 = sequence.get_events_in_range(10.0, 20.0)
        assert len(events_10_to_20) == 0

    def test_sort_events(self):
        """イベントのソート"""
        # 順序が混在したイベント
        unsorted_events = [
            MIDIEvent(2.0, MIDIEventType.NOTE_ON, 60),
            MIDIEvent(0.0, MIDIEventType.SLOT_PRESS, 24),
            MIDIEvent(1.0, MIDIEventType.NOTE_OFF, 60),
            MIDIEvent(1.0, MIDIEventType.NOTE_ON, 52),  # 同じ時刻
        ]
        
        sequence = PlaybackSequence(
            events=unsorted_events,
            total_duration=5.0,
            slot=1,
            tempo=120
        )
        
        sequence.sort_events()
        
        # ソート後の確認
        timestamps = [e.timestamp for e in sequence.events]
        assert timestamps == [0.0, 1.0, 1.0, 2.0]
        
        # 同じ時刻のイベントは、イベントタイプでソートされる
        events_at_1 = [e for e in sequence.events if e.timestamp == 1.0]
        event_types = [e.event_type.value for e in events_at_1]
        assert event_types == sorted(event_types)

    def test_empty_sequence(self):
        """空のシーケンス"""
        empty_sequence = PlaybackSequence(
            events=[],
            total_duration=0.0,
            slot=1,
            tempo=120
        )
        
        assert len(empty_sequence.events) == 0
        assert empty_sequence.get_events_at_time(0.0) == []
        assert empty_sequence.get_events_in_range(0.0, 10.0) == []