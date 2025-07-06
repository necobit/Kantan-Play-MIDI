"""
タイミング計算モジュール
"""
from typing import List


class TimingCalculator:
    """BPMベースのタイミング計算"""

    def __init__(self, tempo: int):
        """
        Args:
            tempo: BPM（Beats Per Minute）
        """
        self.tempo = tempo
        self.seconds_per_beat = 60.0 / tempo

    def calculate_note_timings(self, note_count: int) -> List[float]:
        """
        音符の演奏タイミングを計算
        
        Args:
            note_count: 音符の数
            
        Returns:
            List[float]: 各音符の開始時刻（秒）
        """
        timings = []
        current_time = 0.0
        
        for i in range(note_count):
            timings.append(current_time)
            # 各音符は8回degreeボタンを押すため、8拍分の時間
            note_duration = self.seconds_per_beat * 8
            current_time += note_duration
            
        return timings

    def calculate_degree_press_timings(self, note_start_time: float) -> List[float]:
        """
        1つの音符内でのdegreeボタン押下タイミングを計算
        
        Args:
            note_start_time: 音符の開始時刻
            
        Returns:
            List[float]: 8回のdegreeボタン押下タイミング
        """
        timings = []
        for i in range(8):
            press_time = note_start_time + (i * self.seconds_per_beat)
            timings.append(press_time)
        return timings

    def calculate_slot_timing(self) -> float:
        """
        スロット選択のタイミング（演奏開始前）
        
        Returns:
            float: スロット選択の時刻（常に0.0）
        """
        return 0.0

    def calculate_modifier_timing(self, note_start_time: float) -> float:
        """
        モディファイア押下のタイミング（音符開始と同時）
        
        Args:
            note_start_time: 音符の開始時刻
            
        Returns:
            float: モディファイア押下の時刻
        """
        return note_start_time

    def calculate_modifier_release_timing(self, note_start_time: float) -> float:
        """
        モディファイア解放のタイミング（8拍後）
        
        Args:
            note_start_time: 音符の開始時刻
            
        Returns:
            float: モディファイア解放の時刻
        """
        return note_start_time + (self.seconds_per_beat * 8)

    def get_total_duration(self, note_count: int) -> float:
        """
        全体の演奏時間を計算
        
        Args:
            note_count: 音符の数
            
        Returns:
            float: 演奏時間（秒）
        """
        return note_count * self.seconds_per_beat * 8