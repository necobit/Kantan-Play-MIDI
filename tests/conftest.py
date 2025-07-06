"""
pytestの共通設定とフィクスチャ
"""
import pytest
from pathlib import Path
import json
import tempfile


@pytest.fixture
def sample_midi_config():
    """テスト用のMIDI設定データ"""
    return {
        "slot": [24, 25, 26, 27, 28, 29, 30, 31],
        "notes": [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71],
        "modifier1": [52, 53, 54, 55, 56, 57, 58, 59],
        "modifier2": [52, 53, 54, 55, 56, 57, 58, 59],
        "modifier3": [52, 53, 54, 55, 56, 57, 58, 59]
    }


@pytest.fixture
def temp_midi_config_file(sample_midi_config):
    """一時的なMIDI設定ファイルを作成"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_midi_config, f)
        temp_path = Path(f.name)
    
    yield temp_path
    
    # クリーンアップ
    temp_path.unlink()


@pytest.fixture
def sample_input_json():
    """テスト用の入力JSONデータ"""
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
            },
            {
                "degree": "5",
                "modifier1": 0,
                "modifier2": 1,
                "modifier3": 1
            }
        ]
    }