"""
JSON入力処理モジュール
"""
import json
from pathlib import Path
from typing import Any, Dict, List

from .models import Note, Performance


class InputHandler:
    """JSON入力を処理するクラス"""

    def load_from_file(self, file_path: Path) -> Performance:
        """
        JSONファイルから演奏データを読み込む
        
        Args:
            file_path: JSONファイルのパス
            
        Returns:
            Performance: 演奏データオブジェクト
            
        Raises:
            FileNotFoundError: ファイルが存在しない場合
            json.JSONDecodeError: JSON形式が不正な場合
            ValueError: データ内容が不正な場合
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return self.parse_json_data(data)

    def load_from_string(self, json_string: str) -> Performance:
        """
        JSON文字列から演奏データを読み込む
        
        Args:
            json_string: JSON形式の文字列
            
        Returns:
            Performance: 演奏データオブジェクト
            
        Raises:
            json.JSONDecodeError: JSON形式が不正な場合
            ValueError: データ内容が不正な場合
        """
        data = json.loads(json_string)
        return self.parse_json_data(data)

    def parse_json_data(self, data: Dict[str, Any]) -> Performance:
        """
        JSONデータをPerformanceオブジェクトに変換
        
        Args:
            data: JSONデータ（辞書形式）
            
        Returns:
            Performance: 演奏データオブジェクト
            
        Raises:
            ValueError: 必須フィールドが欠けている場合やデータが不正な場合
        """
        # 必須フィールドの確認
        required_fields = ["slot", "tempo", "notes"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        # notesリストの解析
        notes = self._parse_notes(data["notes"])
        
        # Performanceオブジェクトの作成
        return Performance(
            slot=data["slot"],
            tempo=data["tempo"],
            notes=notes
        )

    def _parse_notes(self, notes_data: List[Dict[str, Any]]) -> List[Note]:
        """
        音符データのリストを解析
        
        Args:
            notes_data: 音符データのリスト（辞書形式）
            
        Returns:
            List[Note]: Noteオブジェクトのリスト
            
        Raises:
            ValueError: 音符データが不正な場合
        """
        if not isinstance(notes_data, list):
            raise ValueError("notes must be a list")
        
        notes = []
        for i, note_data in enumerate(notes_data):
            if not isinstance(note_data, dict):
                raise ValueError(f"Note at index {i} must be a dictionary")
            
            # degreeは必須
            if "degree" not in note_data:
                raise ValueError(f"Note at index {i} is missing 'degree' field")
            
            # Noteオブジェクトの作成
            note = Note(
                degree=note_data["degree"],
                modifier1=note_data.get("modifier1", 0),
                modifier2=note_data.get("modifier2", 0),
                modifier3=note_data.get("modifier3", 0)
            )
            notes.append(note)
        
        return notes

    def validate_performance(self, performance: Performance) -> None:
        """
        演奏データの詳細な検証
        
        Args:
            performance: 検証する演奏データ
            
        Raises:
            ValueError: データが不正な場合
        """
        # Performanceクラスの__post_init__で基本的な検証は行われているが、
        # 追加の検証が必要な場合はここに実装
        
        # 例：演奏時間の推定と警告
        total_beats = len(performance.notes) * 8  # 各音符は8回degreeボタンを押す
        duration_minutes = total_beats / (performance.tempo * 4)  # 4拍で1小節
        
        if duration_minutes > 10:
            import warnings
            warnings.warn(
                f"Performance is very long: approximately {duration_minutes:.1f} minutes"
            )