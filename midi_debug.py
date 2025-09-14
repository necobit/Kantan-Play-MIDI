#!/usr/bin/env python3
"""
MIDI出力の詳細ログを表示するデバッグツール
"""
import time
import threading
from typing import List
import rtmidi

from kantan_play_midi import (
    InputHandler, PerformanceProcessor, MIDIConfig,
    MIDIPlayer, PlaybackState
)

class MIDILogger:
    """MIDI信号の詳細ログを記録"""
    
    def __init__(self):
        self.log_entries = []
        self.start_time = None
    
    def start_logging(self):
        """ログ開始"""
        self.start_time = time.time()
        self.log_entries = []
        print("=== MIDI出力ログ開始 ===")
    
    def log_midi_message(self, message: List[int], description: str = ""):
        """MIDI信号をログに記録"""
        if self.start_time is None:
            return
            
        timestamp = time.time() - self.start_time
        
        # MIDIメッセージの解析
        if len(message) >= 3:
            status = message[0]
            note = message[1]
            velocity = message[2]
            
            if status & 0xF0 == 0x90:  # Note On
                msg_type = "NOTE_ON "
            elif status & 0xF0 == 0x80:  # Note Off
                msg_type = "NOTE_OFF"
            else:
                msg_type = "OTHER   "
            
            channel = (status & 0x0F) + 1
            
            log_entry = {
                'timestamp': timestamp,
                'message': message,
                'type': msg_type,
                'note': note,
                'velocity': velocity,
                'channel': channel,
                'description': description
            }
            
            self.log_entries.append(log_entry)
            
            # リアルタイム表示
            print(f"{timestamp:6.3f}s | {msg_type} | Note:{note:3d} | Vel:{velocity:3d} | Ch:{channel} | {description}")
    
    def print_summary(self):
        """ログの要約を表示"""
        print("\n=== MIDI出力ログ要約 ===")
        print(f"総メッセージ数: {len(self.log_entries)}")
        
        # タイプ別集計
        note_on_count = sum(1 for entry in self.log_entries if entry['type'] == 'NOTE_ON ')
        note_off_count = sum(1 for entry in self.log_entries if entry['type'] == 'NOTE_OFF')
        
        print(f"NOTE_ON:  {note_on_count}")
        print(f"NOTE_OFF: {note_off_count}")
        
        # ノート番号別集計
        notes_used = {}
        for entry in self.log_entries:
            note = entry['note']
            if note not in notes_used:
                notes_used[note] = {'on': 0, 'off': 0}
            if entry['type'] == 'NOTE_ON ':
                notes_used[note]['on'] += 1
            elif entry['type'] == 'NOTE_OFF':
                notes_used[note]['off'] += 1
        
        print("\n使用されたMIDIノート:")
        for note in sorted(notes_used.keys()):
            counts = notes_used[note]
            print(f"  ノート {note:3d}: ON={counts['on']:2d}, OFF={counts['off']:2d}")

class DebuggingMIDIPlayer(MIDIPlayer):
    """ログ機能付きMIDIプレイヤー"""
    
    def __init__(self, logger: MIDILogger, midi_port: str = None):
        super().__init__(midi_port)
        self.logger = logger
    
    def send_note_on(self, note: int, velocity: int = 127) -> None:
        """ノートオン（ログ付き）"""
        message = [0x90 + self.channel, note & 0x7F, velocity & 0x7F]
        self.logger.log_midi_message(message, f"Manual NOTE_ON")
        super().send_note_on(note, velocity)
    
    def send_note_off(self, note: int) -> None:
        """ノートオフ（ログ付き）"""
        message = [0x80 + self.channel, note & 0x7F, 0]
        self.logger.log_midi_message(message, f"Manual NOTE_OFF")
        super().send_note_off(note)
    
    def press_button(self, note: int, duration_ms: int = 50) -> None:
        """ボタン押下（ログ付き）"""
        message_on = [0x90 + self.channel, note & 0x7F, 127]
        message_off = [0x80 + self.channel, note & 0x7F, 0]
        
        self.logger.log_midi_message(message_on, f"Button press (slot)")
        super().send_note_on(note)
        
        time.sleep(duration_ms / 1000.0)
        
        self.logger.log_midi_message(message_off, f"Button release (slot)")
        super().send_note_off(note)

def debug_performance(json_file: str, midi_port: str = None):
    """演奏データのMIDIログを詳細に出力"""
    
    print(f"=== {json_file} のMIDI出力デバッグ ===\n")
    
    # 1. データの読み込み
    from pathlib import Path
    handler = InputHandler()
    performance = handler.load_from_file(Path(json_file))
    
    print(f"スロット: {performance.slot}")
    print(f"テンポ: {performance.tempo} BPM")
    print(f"音符数: {len(performance.notes)}")
    
    # 2. MIDI設定とシーケンス処理
    config = MIDIConfig("MIDI.json")
    processor = PerformanceProcessor(config)
    sequence = processor.process_performance(performance)
    
    print(f"総MIDIイベント数: {len(sequence.events)}")
    print(f"演奏時間: {sequence.total_duration:.2f}秒\n")
    
    # 3. MIDIロガーとプレイヤーの準備
    logger = MIDILogger()
    player = DebuggingMIDIPlayer(logger, midi_port)
    
    try:
        # 4. MIDI接続
        print("MIDIポートに接続中...")
        player.connect(midi_port)
        print(f"接続完了: {player.midi_port}\n")
        
        # 5. ログ開始
        logger.start_logging()
        
        # 6. 演奏実行
        print("演奏開始...\n")
        player.play_sequence(sequence)
        
        # 7. 演奏完了まで待機
        while player.get_state() == PlaybackState.PLAYING:
            time.sleep(0.1)
        
        print("\n演奏完了!")
        
        # 8. ログの要約表示
        logger.print_summary()
        
    except KeyboardInterrupt:
        print("\n演奏中断")
        player.stop()
    except Exception as e:
        print(f"エラー: {e}")
    finally:
        player.disconnect()

def compare_slots():
    """異なるslot値での比較デバッグ"""
    print("=== スロット値による影響の比較 ===\n")
    
    # テストデータ作成
    test_data_slot1 = {
        "slot": 1,
        "tempo": 140,
        "notes": [
            {"degree": "1", "modifier1": 0},
            {"degree": "3", "modifier1": 0},
            {"degree": "5", "modifier1": 0}
        ]
    }
    
    test_data_slot3 = {
        "slot": 3,
        "tempo": 140,
        "notes": [
            {"degree": "1", "modifier1": 0},
            {"degree": "3", "modifier1": 0},
            {"degree": "5", "modifier1": 0}
        ]
    }
    
    import json
    
    # ファイル作成
    with open("test_slot1.json", "w") as f:
        json.dump(test_data_slot1, f, indent=2)
    
    with open("test_slot3.json", "w") as f:
        json.dump(test_data_slot3, f, indent=2)
    
    print("スロット1での演奏:")
    debug_performance("test_slot1.json")
    
    print("\n" + "="*50 + "\n")
    
    print("スロット3での演奏:")
    debug_performance("test_slot3.json")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        midi_port = sys.argv[2] if len(sys.argv) > 2 else None
        debug_performance(json_file, midi_port)
    else:
        # 引数がない場合は比較モード
        compare_slots()