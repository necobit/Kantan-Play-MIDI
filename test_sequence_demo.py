#!/usr/bin/env python3
"""
シーケンス生成のデモスクリプト
"""
from pathlib import Path
from kantan_play_midi import (
    InputHandler, MIDIConfig, PerformanceProcessor
)


def demo_sequence_generation():
    print("=== MIDI変換処理デモ ===\n")
    
    # 1. 入力データの読み込み
    print("1. JSONファイルの読み込み")
    handler = InputHandler()
    performance = handler.load_from_file(Path("example_input.json"))
    print(f"   スロット: {performance.slot}")
    print(f"   テンポ: {performance.tempo} BPM")
    print(f"   音符数: {len(performance.notes)}")
    print()
    
    # 2. MIDI設定の読み込み
    print("2. MIDI設定の読み込み")
    config = MIDIConfig(Path("MIDI.json"))
    print(f"   スロット用ノート: {config.slot_notes[:3]}...")
    print(f"   音階用ノート: {config.degree_notes[:3]}...")
    print()
    
    # 3. シーケンス生成
    print("3. 演奏シーケンスの生成")
    processor = PerformanceProcessor(config)
    sequence = processor.process_performance(performance)
    print(f"   総イベント数: {len(sequence.events)}")
    print(f"   総演奏時間: {sequence.total_duration:.2f}秒")
    print()
    
    # 4. シーケンス概要の表示
    print("4. シーケンス概要")
    summary = processor.get_sequence_summary(sequence)
    print(summary)
    print()
    
    # 5. イベントの詳細（最初の10個）
    print("5. イベント詳細（最初の10個）")
    for i, event in enumerate(sequence.events[:10]):
        print(f"   {i+1:2d}. {event.timestamp:6.3f}s "
              f"{event.event_type.value:12s} "
              f"note={event.note:2d} "
              f"| {event.description}")
    
    if len(sequence.events) > 10:
        print(f"   ... 他 {len(sequence.events) - 10} イベント")
    
    print("\n✅ シーケンス生成が完了しました！")


if __name__ == "__main__":
    try:
        demo_sequence_generation()
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()