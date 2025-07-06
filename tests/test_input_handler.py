"""
入力処理のテスト
"""
import json
import tempfile
from pathlib import Path

import pytest

from kantan_play_midi.input_handler import InputHandler
from kantan_play_midi.models import Note, Performance


class TestInputHandler:
    """InputHandlerクラスのテスト"""

    @pytest.fixture
    def handler(self):
        """InputHandlerのインスタンス"""
        return InputHandler()

    @pytest.fixture
    def valid_json_data(self):
        """有効なJSONデータ"""
        return {
            "slot": 1,
            "tempo": 120,
            "notes": [
                {
                    "degree": "1",
                    "modifier1": 0,
                    "modifier2": 0,
                    "modifier3": 0
                },
                {
                    "degree": "3",
                    "modifier1": 1,
                    "modifier2": 0,
                    "modifier3": 0
                }
            ]
        }

    def test_load_from_file_success(self, handler, valid_json_data):
        """ファイルからの正常な読み込み"""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(valid_json_data, f)
            temp_path = Path(f.name)

        try:
            performance = handler.load_from_file(temp_path)
            assert performance.slot == 1
            assert performance.tempo == 120
            assert len(performance.notes) == 2
            assert performance.notes[0].degree == "1"
            assert performance.notes[1].degree == "3"
        finally:
            temp_path.unlink()

    def test_load_from_file_not_found(self, handler):
        """存在しないファイルの場合"""
        with pytest.raises(FileNotFoundError):
            handler.load_from_file(Path("nonexistent.json"))

    def test_load_from_string_success(self, handler, valid_json_data):
        """文字列からの正常な読み込み"""
        json_string = json.dumps(valid_json_data)
        performance = handler.load_from_string(json_string)
        assert performance.slot == 1
        assert performance.tempo == 120
        assert len(performance.notes) == 2

    def test_load_from_string_invalid_json(self, handler):
        """不正なJSON文字列の場合"""
        with pytest.raises(json.JSONDecodeError):
            handler.load_from_string("invalid json")

    def test_parse_json_missing_fields(self, handler):
        """必須フィールドが欠けている場合"""
        # slotが欠けている
        with pytest.raises(ValueError, match="Missing required fields.*slot"):
            handler.parse_json_data({"tempo": 120, "notes": []})

        # tempoが欠けている
        with pytest.raises(ValueError, match="Missing required fields.*tempo"):
            handler.parse_json_data({"slot": 1, "notes": []})

        # notesが欠けている
        with pytest.raises(ValueError, match="Missing required fields.*notes"):
            handler.parse_json_data({"slot": 1, "tempo": 120})

    def test_parse_notes_invalid_format(self, handler):
        """notesフィールドの形式が不正な場合"""
        # notesがリストでない
        with pytest.raises(ValueError, match="notes must be a list"):
            handler.parse_json_data({
                "slot": 1,
                "tempo": 120,
                "notes": "not a list"
            })

        # note要素が辞書でない
        with pytest.raises(ValueError, match="must be a dictionary"):
            handler.parse_json_data({
                "slot": 1,
                "tempo": 120,
                "notes": ["not a dict"]
            })

        # degreeフィールドが欠けている
        with pytest.raises(ValueError, match="missing 'degree' field"):
            handler.parse_json_data({
                "slot": 1,
                "tempo": 120,
                "notes": [{"modifier1": 0}]
            })

    def test_parse_notes_with_defaults(self, handler):
        """モディファイアのデフォルト値のテスト"""
        data = {
            "slot": 1,
            "tempo": 120,
            "notes": [{"degree": "1"}]  # modifierは省略
        }
        performance = handler.parse_json_data(data)
        note = performance.notes[0]
        assert note.modifier1 == 0
        assert note.modifier2 == 0
        assert note.modifier3 == 0

    def test_validate_performance_long_duration_warning(self, handler):
        """長時間の演奏に対する警告"""
        # 非常に多くの音符を持つ演奏データ
        notes = [Note(degree="1") for _ in range(100)]
        performance = Performance(slot=1, tempo=60, notes=notes)
        
        # 警告が発生することを確認
        with pytest.warns(UserWarning, match="Performance is very long"):
            handler.validate_performance(performance)

    def test_complex_performance_data(self, handler):
        """複雑な演奏データの処理"""
        data = {
            "slot": 8,
            "tempo": 180,
            "notes": [
                {"degree": "1", "modifier1": 0, "modifier2": 0, "modifier3": 0},
                {"degree": "2b", "modifier1": 1, "modifier2": 2, "modifier3": 3},
                {"degree": "3", "modifier1": 4, "modifier2": 5, "modifier3": 6},
                {"degree": "4", "modifier1": 7, "modifier2": 8, "modifier3": 0},
                {"degree": "5b", "modifier1": 1, "modifier2": 0, "modifier3": 1},
                {"degree": "6", "modifier1": 0, "modifier2": 1, "modifier3": 0},
                {"degree": "7b", "modifier1": 2, "modifier2": 2, "modifier3": 2},
                {"degree": "7", "modifier1": 8, "modifier2": 8, "modifier3": 8}
            ]
        }
        performance = handler.parse_json_data(data)
        assert performance.slot == 8
        assert performance.tempo == 180
        assert len(performance.notes) == 8
        
        # 各音符の内容を確認
        assert performance.notes[1].degree == "2b"
        assert performance.notes[1].modifier1 == 1
        assert performance.notes[1].modifier2 == 2
        assert performance.notes[1].modifier3 == 3