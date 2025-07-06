"""
タイミング計算のテスト
"""
import pytest

from kantan_play_midi.timing import TimingCalculator


class TestTimingCalculator:
    """TimingCalculatorクラスのテスト"""

    def test_initialization(self):
        """初期化のテスト"""
        calc = TimingCalculator(120)
        assert calc.tempo == 120
        assert calc.seconds_per_beat == 0.5  # 60/120 = 0.5

    def test_calculate_note_timings(self):
        """音符タイミング計算のテスト"""
        calc = TimingCalculator(60)  # 1秒 = 1拍
        
        # 3音符の場合
        timings = calc.calculate_note_timings(3)
        
        assert len(timings) == 3
        assert timings[0] == 0.0      # 1音符目: 0秒
        assert timings[1] == 8.0      # 2音符目: 8秒後
        assert timings[2] == 16.0     # 3音符目: 16秒後

    def test_calculate_degree_press_timings(self):
        """degreeボタン押下タイミングのテスト"""
        calc = TimingCalculator(60)  # 1秒 = 1拍
        
        timings = calc.calculate_degree_press_timings(10.0)
        
        assert len(timings) == 8
        expected = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0]
        for expected_time, actual_time in zip(expected, timings):
            assert abs(expected_time - actual_time) < 0.001

    def test_calculate_slot_timing(self):
        """スロット選択タイミングのテスト"""
        calc = TimingCalculator(120)
        assert calc.calculate_slot_timing() == 0.0

    def test_calculate_modifier_timing(self):
        """モディファイアタイミングのテスト"""
        calc = TimingCalculator(120)
        note_start = 5.0
        
        assert calc.calculate_modifier_timing(note_start) == 5.0
        assert calc.calculate_modifier_release_timing(note_start) == 9.0  # 5.0 + 4.0 (8拍 * 0.5秒/拍)

    def test_get_total_duration(self):
        """総演奏時間計算のテスト"""
        calc = TimingCalculator(60)  # 1秒 = 1拍
        
        assert calc.get_total_duration(1) == 8.0   # 1音符 = 8拍 = 8秒
        assert calc.get_total_duration(3) == 24.0  # 3音符 = 24拍 = 24秒

    def test_different_tempos(self):
        """異なるテンポでのテスト"""
        # テンポ120の場合
        calc_120 = TimingCalculator(120)
        timings_120 = calc_120.calculate_note_timings(2)
        
        # テンポ60の場合
        calc_60 = TimingCalculator(60)
        timings_60 = calc_60.calculate_note_timings(2)
        
        # テンポが2倍なら、時間は半分になる
        assert timings_120[1] == timings_60[1] / 2