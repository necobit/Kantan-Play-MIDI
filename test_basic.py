#!/usr/bin/env python3
"""
基本的な動作確認スクリプト
"""
from pathlib import Path
from src.kantan_play_midi import MIDIConfig, MIDIConverter

def test_basic_functionality():
    print("=== Kantan Play MIDI 動作確認 ===\n")
    
    # 1. MIDI設定の読み込み
    print("1. MIDI.json設定の読み込み")
    config_path = Path("MIDI.json")
    config = MIDIConfig(config_path)
    
    print(f"  - スロット用ノート: {config.slot_notes}")
    print(f"  - 音階用ノート: {config.degree_notes}")
    print(f"  - Modifier1ノート: {config.modifier1_notes}\n")
    
    # 2. 変換テスト
    print("2. 変換機能のテスト")
    converter = MIDIConverter(config)
    
    # スロット変換
    print("  [スロット変換]")
    for slot in [1, 3, 8]:
        note = converter.convert_slot(slot)
        print(f"    スロット {slot} → MIDIノート {note}")
    
    # 音階変換
    print("\n  [音階変換]")
    for degree in ["1", "3b", "5", "7"]:
        note = converter.convert_degree(degree)
        print(f"    音階 {degree} → MIDIノート {note}")
    
    # モディファイア変換
    print("\n  [モディファイア変換]")
    for mod_num in [1, 2, 3]:
        note = converter.convert_modifier(mod_num, 1)
        print(f"    Modifier{mod_num} (値=1) → MIDIノート {note}")
    
    print("\n3. サンプル演奏データの変換")
    sample_notes = [
        {"degree": "1", "modifier1": 0, "modifier2": 0, "modifier3": 0},
        {"degree": "3", "modifier1": 1, "modifier2": 0, "modifier3": 0},
        {"degree": "5", "modifier1": 0, "modifier2": 1, "modifier3": 1}
    ]
    
    for i, note_data in enumerate(sample_notes, 1):
        print(f"\n  音符 {i}:")
        degree_note = converter.convert_degree(note_data["degree"])
        print(f"    音階: {note_data['degree']} → MIDIノート {degree_note}")
        
        modifiers = []
        for mod_num in [1, 2, 3]:
            mod_value = note_data[f"modifier{mod_num}"]
            if mod_value > 0:
                mod_note = converter.convert_modifier(mod_num, mod_value)
                modifiers.append(f"Modifier{mod_num}={mod_note}")
        
        if modifiers:
            print(f"    モディファイア: {', '.join(modifiers)}")
        else:
            print("    モディファイア: なし")

if __name__ == "__main__":
    try:
        test_basic_functionality()
        print("\n✅ 基本機能の動作確認が完了しました！")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()