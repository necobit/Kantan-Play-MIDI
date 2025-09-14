#!/usr/bin/env python3
"""
MIDI送信のデバッグスクリプト
実際に送信されるMIDI信号を詳細表示
"""
import time
import rtmidi

def debug_midi_output():
    """MIDI出力のデバッグ"""
    print("=== MIDI出力デバッグ ===")
    
    # MIDIアウトポートを作成
    midi_out = rtmidi.MidiOut()
    ports = midi_out.get_ports()
    
    print(f"利用可能ポート: {ports}")
    
    if not ports:
        print("MIDIポートがありません")
        return
    
    # 最初のポートに接続
    port_name = ports[0]
    midi_out.open_port(0)
    print(f"接続済み: {port_name}")
    
    # テストMIDI信号を送信
    test_notes = [60, 62, 64, 65]  # C, D, E, F
    
    print("\n=== MIDI信号送信開始 ===")
    for i, note in enumerate(test_notes):
        print(f"[{i+1}/4] ノート {note} を送信")
        
        # ノートオン
        note_on = [0x90, note, 100]  # チャンネル1, ノート, ベロシティ100
        print(f"  ノートオン: {note_on}")
        midi_out.send_message(note_on)
        
        time.sleep(0.5)  # 0.5秒間鳴らす
        
        # ノートオフ
        note_off = [0x80, note, 0]
        print(f"  ノートオフ: {note_off}")
        midi_out.send_message(note_off)
        
        time.sleep(0.2)  # 0.2秒の間隔
    
    print("\n=== 送信完了 ===")
    
    # クリーンアップ
    midi_out.close_port()
    midi_out.delete()

if __name__ == "__main__":
    debug_midi_output()