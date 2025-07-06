# API仕様書

このドキュメントでは、Kantan Play MIDIのプログラミングインターフェース（API）について詳しく説明します。

## パッケージ概要

```python
import kantan_play_midi
```

### 主要モジュール

| モジュール | 説明 |
|-----------|------|
| `kantan_play_midi.MIDIPlayer` | MIDI演奏制御 |
| `kantan_play_midi.InputHandler` | JSON入力処理 |
| `kantan_play_midi.PerformanceProcessor` | 演奏データ処理 |
| `kantan_play_midi.MIDIConfig` | MIDI設定管理 |
| `kantan_play_midi.models` | データモデル |
| `kantan_play_midi.exceptions` | 例外クラス |

## データモデル

### Note クラス

音符を表現するデータクラス。

```python
from kantan_play_midi.models import Note

note = Note(
    degree="3",
    modifier1=1,
    modifier2=0,
    modifier3=2
)
```

#### 属性

| 属性 | 型 | 説明 | デフォルト |
|------|----|----|-----------|
| `degree` | str | 音階 ("1", "2b", "2", ..., "7") | 必須 |
| `modifier1` | int | モディファイア1 (0-8) | 0 |
| `modifier2` | int | モディファイア2 (0-8) | 0 |
| `modifier3` | int | モディファイア3 (0-8) | 0 |

#### メソッド

```python
# 検証
note.validate()  # バリデーション実行

# 辞書変換
note_dict = note.to_dict()
```

### Performance クラス

演奏全体を表現するデータクラス。

```python
from kantan_play_midi.models import Performance, Note

performance = Performance(
    slot=1,
    tempo=120,
    notes=[
        Note(degree="1"),
        Note(degree="3", modifier1=1),
        Note(degree="5")
    ]
)
```

#### 属性

| 属性 | 型 | 説明 |
|------|----|----|
| `slot` | int | スロット番号 (1-8) |
| `tempo` | int | テンポ (BPM) |
| `notes` | List[Note] | 音符のリスト |

## MIDI演奏制御

### MIDIPlayer クラス

MIDI演奏の中核となるクラス。

```python
from kantan_play_midi import MIDIPlayer, PlaybackState

# プレイヤーの作成
player = MIDIPlayer()

# MIDIポートの取得
ports = player.get_available_ports()
print(f"利用可能ポート: {ports}")

# 接続
player.connect("M2")  # または player.connect() で自動選択

# 演奏状態の確認
state = player.get_state()
print(f"現在の状態: {state}")
```

#### 主要メソッド

##### `get_available_ports() -> List[str]`
利用可能なMIDIポートのリストを取得。

```python
ports = player.get_available_ports()
# 戻り値例: ["M2", "IAC Driver Bus 1", "USB MIDI Device"]
```

##### `connect(port_name: Optional[str] = None) -> None`
MIDIポートに接続。

```python
# 特定ポート指定
player.connect("M2")

# 自動選択（最初の利用可能ポート）
player.connect()
```

**例外**:
- `MIDIDeviceError`: 接続失敗時

##### `disconnect() -> None`
MIDIポートから切断。

```python
player.disconnect()
```

##### `is_connected() -> bool`
接続状態を確認。

```python
if player.is_connected():
    print("MIDI接続中")
```

##### `send_note_on(note: int, velocity: int = 127) -> None`
ノートオン信号を送信。

```python
player.send_note_on(60, 100)  # C4、ベロシティ100
```

##### `send_note_off(note: int) -> None`
ノートオフ信号を送信。

```python
player.send_note_off(60)  # C4停止
```

##### `press_button(note: int, duration_ms: int = 50) -> None`
ボタン押下をシミュレート。

```python
player.press_button(60, 100)  # 100ms間C4ボタンを押下
```

##### `play_sequence(sequence: PlaybackSequence) -> None`
シーケンスの演奏を開始。

```python
# シーケンスの作成（後述）
sequence = processor.process_performance(performance)

# 演奏開始
player.play_sequence(sequence)
```

##### `pause() -> None` / `resume() -> None` / `stop() -> None`
演奏制御。

```python
player.pause()   # 一時停止
player.resume()  # 再開
player.stop()    # 停止
```

##### `get_state() -> PlaybackState`
現在の演奏状態を取得。

```python
from kantan_play_midi import PlaybackState

state = player.get_state()

if state == PlaybackState.PLAYING:
    print("演奏中")
elif state == PlaybackState.PAUSED:
    print("一時停止中")
elif state == PlaybackState.STOPPED:
    print("停止中")
```

##### `get_current_time() -> float`
現在の演奏時刻を取得（秒）。

```python
current_time = player.get_current_time()
print(f"演奏時刻: {current_time:.1f}秒")
```

## 入力処理

### InputHandler クラス

JSON入力の読み込みと検証を担当。

```python
from kantan_play_midi import InputHandler

handler = InputHandler()
```

#### 主要メソッド

##### `load_from_file(file_path: Path) -> Performance`
JSONファイルから演奏データを読み込み。

```python
from pathlib import Path

performance = handler.load_from_file(Path("song.json"))
```

**例外**:
- `InvalidInputError`: ファイルが見つからない、JSON形式エラー
- `ValueError`: 必須フィールドの欠落

##### `load_from_string(json_string: str) -> Performance`
JSON文字列から演奏データを読み込み。

```python
json_data = '''
{
  "slot": 1,
  "tempo": 120,
  "notes": [{"degree": "1"}]
}
'''

performance = handler.load_from_string(json_data)
```

##### `validate_performance(performance: Performance) -> None`
演奏データの詳細検証。

```python
try:
    handler.validate_performance(performance)
    print("検証成功")
except InvalidInputError as e:
    print(f"検証エラー: {e}")
```

## 演奏処理

### PerformanceProcessor クラス

演奏データをMIDIシーケンスに変換。

```python
from kantan_play_midi import PerformanceProcessor, MIDIConfig

# MIDI設定の読み込み
config = MIDIConfig("MIDI.json")

# プロセッサの作成
processor = PerformanceProcessor(config)

# 演奏データの処理
sequence = processor.process_performance(performance)
```

#### 主要メソッド

##### `process_performance(performance: Performance) -> PlaybackSequence`
演奏データをMIDIシーケンスに変換。

```python
sequence = processor.process_performance(performance)

print(f"総イベント数: {len(sequence.events)}")
print(f"演奏時間: {sequence.total_duration:.2f}秒")
```

## MIDI設定

### MIDIConfig クラス

MIDI設定ファイルの管理。

```python
from kantan_play_midi import MIDIConfig

# 設定ファイルの読み込み
config = MIDIConfig("MIDI.json")

# 設定値の取得
slot_notes = config.slot_mapping
degree_notes = config.degree_mapping
```

#### 主要属性

| 属性 | 型 | 説明 |
|------|----|----|
| `slot_mapping` | List[int] | スロットのMIDIノート番号 |
| `degree_mapping` | Dict[str, int] | 音階のMIDIノート番号 |
| `modifier_mappings` | Dict[int, List[int]] | モディファイアのMIDIノート番号 |

## MIDIシーケンス

### PlaybackSequence クラス

演奏可能なMIDIイベントのシーケンス。

```python
from kantan_play_midi.sequence import PlaybackSequence, MIDIEvent, MIDIEventType

# イベントの作成
events = [
    MIDIEvent(0.0, MIDIEventType.NOTE_ON, 60),
    MIDIEvent(0.1, MIDIEventType.NOTE_OFF, 60),
]

# シーケンスの作成
sequence = PlaybackSequence(
    events=events,
    total_duration=1.0,
    slot=1,
    tempo=120
)
```

### MIDIEvent クラス

個別のMIDIイベント。

```python
from kantan_play_midi.sequence import MIDIEvent, MIDIEventType

event = MIDIEvent(
    timestamp=0.5,           # 実行時刻（秒）
    event_type=MIDIEventType.NOTE_ON,
    note=60,                 # MIDIノート番号
    velocity=127,            # ベロシティ
    duration=0.1             # 持続時間（slot_pressのみ）
)
```

#### MIDIEventType 列挙型

```python
from kantan_play_midi.sequence import MIDIEventType

# 利用可能な種類
MIDIEventType.NOTE_ON      # ノートオン
MIDIEventType.NOTE_OFF     # ノートオフ
MIDIEventType.SLOT_PRESS   # スロット押下
```

## 例外処理

### カスタム例外

```python
from kantan_play_midi.exceptions import (
    KantanPlayMIDIError,
    InvalidInputError,
    MIDIDeviceError,
    ConfigurationError
)

try:
    performance = handler.load_from_file("invalid.json")
except InvalidInputError as e:
    print(f"入力エラー: {e}")
except ConfigurationError as e:
    print(f"設定エラー: {e}")
except KantanPlayMIDIError as e:
    print(f"一般エラー: {e}")
```

#### 例外階層

```
KantanPlayMIDIError (基底クラス)
├── InvalidInputError (入力データエラー)
├── MIDIDeviceError (MIDIデバイスエラー)
└── ConfigurationError (設定ファイルエラー)
```

## 完全な使用例

### 基本的な演奏

```python
from kantan_play_midi import (
    MIDIPlayer, InputHandler, PerformanceProcessor, MIDIConfig
)

def play_song(json_file: str, midi_port: str = None):
    # 1. 入力データの読み込み
    handler = InputHandler()
    performance = handler.load_from_file(json_file)
    
    # 2. MIDI設定の読み込み
    config = MIDIConfig("MIDI.json")
    
    # 3. 演奏データの処理
    processor = PerformanceProcessor(config)
    sequence = processor.process_performance(performance)
    
    # 4. MIDI演奏
    player = MIDIPlayer()
    try:
        player.connect(midi_port)
        player.play_sequence(sequence)
        
        # 演奏完了まで待機
        while player.get_state() == PlaybackState.PLAYING:
            time.sleep(0.1)
            
    finally:
        player.disconnect()

# 使用例
play_song("song.json", "M2")
```

### リアルタイム制御

```python
import time
from kantan_play_midi import MIDIPlayer, PlaybackState

def controlled_playback(sequence):
    player = MIDIPlayer()
    player.connect()
    
    try:
        player.play_sequence(sequence)
        
        # 3秒後に一時停止
        time.sleep(3.0)
        player.pause()
        print("一時停止")
        
        # 2秒後に再開
        time.sleep(2.0)
        player.resume()
        print("再開")
        
        # 演奏完了まで待機
        while player.get_state() == PlaybackState.PLAYING:
            current_time = player.get_current_time()
            total_time = sequence.total_duration
            progress = (current_time / total_time) * 100
            print(f"\r進行: {progress:.1f}%", end="")
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        player.stop()
        print("\n演奏中断")
    finally:
        player.disconnect()
```

### カスタムMIDI設定

```python
def create_custom_config():
    # カスタム設定の作成
    custom_config = {
        "slot": [36, 37, 38, 39, 40, 41, 42, 43],      # キック系
        "notes": [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79],  # ピアノ系
        "modifier1": [48, 49, 50, 51, 52, 53, 54, 55], # ベース系
        "modifier2": [56, 57, 58, 59, 60, 61, 62, 63], # リード系
        "modifier3": [64, 65, 66, 67, 68, 69, 70, 71]  # パッド系
    }
    
    # ファイルに保存
    import json
    with open("custom_midi.json", "w") as f:
        json.dump(custom_config, f, indent=2)
    
    return MIDIConfig("custom_midi.json")
```

### バッチ処理

```python
from pathlib import Path

def batch_process(input_dir: str, output_dir: str):
    """複数のJSONファイルを一括処理"""
    handler = InputHandler()
    config = MIDIConfig("MIDI.json")
    processor = PerformanceProcessor(config)
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for json_file in input_path.glob("*.json"):
        try:
            # 処理
            performance = handler.load_from_file(json_file)
            sequence = processor.process_performance(performance)
            
            # 結果の保存（例：統計情報）
            stats = {
                "file": json_file.name,
                "duration": sequence.total_duration,
                "events": len(sequence.events),
                "slot": performance.slot,
                "tempo": performance.tempo
            }
            
            output_file = output_path / f"{json_file.stem}_stats.json"
            with open(output_file, "w") as f:
                json.dump(stats, f, indent=2)
                
            print(f"処理完了: {json_file.name}")
            
        except Exception as e:
            print(f"エラー in {json_file.name}: {e}")

# 使用例
batch_process("songs/", "output/")
```

## パフォーマンス考慮事項

### メモリ使用量

- **大きなシーケンス**: 長時間の演奏では大量のMIDIEventが生成される
- **推奨**: 演奏時間5分以内、1000イベント以下

### CPU使用量

- **リアルタイム演奏**: 高精度タイミングでCPU使用量が増加
- **推奨**: 他の重い処理との同時実行を避ける

### MIDI遅延

- **USBレイテンシ**: USBーMIDIインターフェースで1-5ms程度
- **システム負荷**: CPUやI/O負荷で遅延が増加

## トラブルシューティング

### よくあるエラーと対処法

#### 1. `ModuleNotFoundError: No module named 'kantan_play_midi'`

```python
# パッケージの再インストール
pip install -e .
```

#### 2. `MIDIDeviceError: MIDI device not connected`

```python
# 接続確認
player = MIDIPlayer()
ports = player.get_available_ports()
print(f"利用可能ポート: {ports}")

if ports:
    player.connect(ports[0])
else:
    print("MIDIポートが見つかりません")
```

#### 3. `InvalidInputError: Invalid JSON format`

```python
# JSON構文チェック
import json

try:
    with open("song.json") as f:
        data = json.load(f)
    print("JSON形式は正しいです")
except json.JSONDecodeError as e:
    print(f"JSON構文エラー: {e}")
```

## 関連情報

- [ユーザーガイド](user_guide.md) - 基本的な使用方法
- [インストールガイド](installation.md) - 環境構築
- [GitHub Repository](https://github.com/necobit/Kantan-Play-MIDI) - ソースコード