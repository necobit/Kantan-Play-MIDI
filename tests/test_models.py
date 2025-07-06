"""
モデルクラスのテスト
"""
import pytest

from kantan_play_midi.models import Note, Performance


class TestNote:
    """Noteクラスのテスト"""

    def test_valid_note_creation(self):
        """正常なNoteオブジェクトの作成"""
        note = Note(degree="1", modifier1=0, modifier2=0, modifier3=0)
        assert note.degree == "1"
        assert note.modifier1 == 0
        assert note.modifier2 == 0
        assert note.modifier3 == 0

    def test_note_with_modifiers(self):
        """モディファイア付きのNote作成"""
        note = Note(degree="5", modifier1=3, modifier2=7, modifier3=1)
        assert note.degree == "5"
        assert note.modifier1 == 3
        assert note.modifier2 == 7
        assert note.modifier3 == 1

    def test_flat_degrees(self):
        """フラット付き音階のテスト"""
        for degree in ["2b", "3b", "5b", "6b", "7b"]:
            note = Note(degree=degree)
            assert note.degree == degree

    def test_invalid_degree(self):
        """無効な音階での例外"""
        with pytest.raises(ValueError, match="Invalid degree"):
            Note(degree="8")

    def test_invalid_modifier_values(self):
        """無効なモディファイア値での例外"""
        with pytest.raises(ValueError, match="modifier1 must be between"):
            Note(degree="1", modifier1=-1)

        with pytest.raises(ValueError, match="modifier2 must be between"):
            Note(degree="1", modifier2=9)

        with pytest.raises(ValueError, match="modifier3 must be between"):
            Note(degree="1", modifier3=10)


class TestPerformance:
    """Performanceクラスのテスト"""

    def test_valid_performance_creation(self):
        """正常なPerformanceオブジェクトの作成"""
        notes = [
            Note(degree="1"),
            Note(degree="3", modifier1=1),
            Note(degree="5", modifier2=1, modifier3=1)
        ]
        perf = Performance(slot=1, tempo=120, notes=notes)
        assert perf.slot == 1
        assert perf.tempo == 120
        assert len(perf.notes) == 3

    def test_slot_validation(self):
        """スロット番号の検証"""
        notes = [Note(degree="1")]
        
        # 有効な範囲
        for slot in range(1, 9):
            perf = Performance(slot=slot, tempo=120, notes=notes)
            assert perf.slot == slot

        # 無効な値
        with pytest.raises(ValueError, match="slot must be between"):
            Performance(slot=0, tempo=120, notes=notes)

        with pytest.raises(ValueError, match="slot must be between"):
            Performance(slot=9, tempo=120, notes=notes)

    def test_tempo_validation(self):
        """テンポの検証"""
        notes = [Note(degree="1")]
        
        # 有効な範囲
        for tempo in [20, 60, 120, 180, 600]:
            perf = Performance(slot=1, tempo=tempo, notes=notes)
            assert perf.tempo == tempo

        # 無効な値
        with pytest.raises(ValueError, match="tempo must be between"):
            Performance(slot=1, tempo=19, notes=notes)

        with pytest.raises(ValueError, match="tempo must be between"):
            Performance(slot=1, tempo=601, notes=notes)

    def test_empty_notes_list(self):
        """空のnotesリストでの例外"""
        with pytest.raises(ValueError, match="notes list cannot be empty"):
            Performance(slot=1, tempo=120, notes=[])