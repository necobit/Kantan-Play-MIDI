"""
パフォーマンス処理のテスト
"""
import pytest

from kantan_play_midi.models import Note, Performance
from kantan_play_midi.config import MIDIConfig
from kantan_play_midi.processor import PerformanceProcessor
from kantan_play_midi.sequence import MIDIEventType


class TestPerformanceProcessor:
    """PerformanceProcessorクラスのテスト"""

    @pytest.fixture
    def config(self, temp_midi_config_file):
        """MIDI設定のフィクスチャ"""
        return MIDIConfig(temp_midi_config_file)

    @pytest.fixture
    def processor(self, config):
        """PerformanceProcessorのインスタンス"""
        return PerformanceProcessor(config)

    @pytest.fixture
    def simple_performance(self):
        """シンプルな演奏データ"""
        return Performance(
            slot=1,
            tempo=120,
            notes=[
                Note(degree="1"),
                Note(degree="3", modifier1=1)
            ]
        )

    def test_process_simple_performance(self, processor, simple_performance):
        """シンプルな演奏データの処理"""
        sequence = processor.process_performance(simple_performance)
        
        # 基本的な検証
        assert sequence.slot == 1
        assert sequence.tempo == 120
        assert sequence.total_duration > 0
        assert len(sequence.events) > 0

    def test_slot_event_creation(self, processor, simple_performance):
        """スロット選択イベントの作成"""
        sequence = processor.process_performance(simple_performance)
        
        # スロットイベントの確認
        slot_events = [e for e in sequence.events if e.event_type == MIDIEventType.SLOT_PRESS]
        assert len(slot_events) == 1
        
        slot_event = slot_events[0]
        assert slot_event.timestamp == 0.0
        assert slot_event.note == 24  # slot 1 -> MIDI note 24
        assert slot_event.duration == 0.05

    def test_note_events_creation(self, processor, simple_performance):
        """音符イベントの作成"""
        sequence = processor.process_performance(simple_performance)
        
        # ノートオン/オフイベントの確認
        note_on_events = [e for e in sequence.events if e.event_type == MIDIEventType.NOTE_ON]
        note_off_events = [e for e in sequence.events if e.event_type == MIDIEventType.NOTE_OFF]
        
        # 音符1（degree="1"）: 8回のdegree押下 = 8回のon/off
        # 音符2（degree="3", modifier1=1）: 1回のmodifier + 8回のdegree = 9回のon/off
        # 合計: 17回のon, 17回のoff
        assert len(note_on_events) == 17
        assert len(note_off_events) == 17

    def test_modifier_handling(self, processor):
        """モディファイア処理のテスト"""
        performance = Performance(
            slot=1,
            tempo=120,
            notes=[Note(degree="1", modifier1=2, modifier2=3, modifier3=0)]
        )
        
        sequence = processor.process_performance(performance)
        
        # モディファイア関連のイベントを確認
        modifier_events = [
            e for e in sequence.events 
            if e.note in [53, 54] and e.event_type == MIDIEventType.NOTE_ON  # modifier1=2->53, modifier2=3->54
        ]
        assert len(modifier_events) == 2  # modifier1とmodifier2のみ

    def test_timing_calculation(self, processor):
        """タイミング計算のテスト"""
        performance = Performance(
            slot=1,
            tempo=60,  # 1秒 = 1拍
            notes=[Note(degree="1")]
        )
        
        sequence = processor.process_performance(performance)
        
        # 1音符 = 8拍 = 8秒
        assert sequence.total_duration == 8.0
        
        # degree押下タイミング（0, 1, 2, 3, 4, 5, 6, 7秒）
        degree_events = [
            e for e in sequence.events 
            if e.event_type == MIDIEventType.NOTE_ON and e.note == 60  # degree="1" -> 60
        ]
        
        expected_timings = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
        actual_timings = [e.timestamp for e in degree_events]
        
        for expected, actual in zip(expected_timings, actual_timings):
            assert abs(expected - actual) < 0.001

    def test_event_ordering(self, processor, simple_performance):
        """イベントの順序が正しいことを確認"""
        sequence = processor.process_performance(simple_performance)
        
        # イベントが時刻順にソートされていることを確認
        timestamps = [e.timestamp for e in sequence.events]
        assert timestamps == sorted(timestamps)

    def test_complex_performance(self, processor):
        """複雑な演奏データの処理"""
        performance = Performance(
            slot=5,
            tempo=180,
            notes=[
                Note(degree="2b", modifier1=1, modifier2=2),
                Note(degree="5", modifier3=3),
                Note(degree="7b", modifier1=4, modifier2=5, modifier3=6)
            ]
        )
        
        sequence = processor.process_performance(performance)
        
        # 基本的な検証
        assert sequence.slot == 5
        assert sequence.tempo == 180
        assert len(sequence.events) > 0
        
        # スロットイベントの確認
        slot_events = [e for e in sequence.events if e.event_type == MIDIEventType.SLOT_PRESS]
        assert len(slot_events) == 1
        assert slot_events[0].note == 28  # slot 5 -> MIDI note 28

    def test_sequence_summary(self, processor, simple_performance):
        """シーケンス概要の生成"""
        sequence = processor.process_performance(simple_performance)
        summary = processor.get_sequence_summary(sequence)
        
        assert "演奏シーケンス概要" in summary
        assert "スロット: 1" in summary
        assert "テンポ: 120 BPM" in summary
        assert "総演奏時間" in summary
        assert "イベント内訳" in summary

    def test_invalid_performance_data(self, processor):
        """無効な演奏データの処理"""
        # 無効なスロット
        with pytest.raises(ValueError, match="Invalid slot"):
            performance = Performance(slot=10, tempo=120, notes=[Note(degree="1")])
            processor.process_performance(performance)

        # 無効な音階
        with pytest.raises(ValueError, match="Invalid degree"):
            performance = Performance(slot=1, tempo=120, notes=[Note(degree="invalid")])
            processor.process_performance(performance)