"""
MIDI演奏制御モジュール
"""
from typing import List, Optional, Dict, Any
import time
import threading
from enum import Enum

import rtmidi

from .exceptions import MIDIDeviceError
from .sequence import PlaybackSequence, MIDIEvent, MIDIEventType


class PlaybackState(Enum):
    """演奏状態"""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


class MIDIPlayer:
    """MIDI演奏を制御するクラス"""

    def __init__(self, midi_port: Optional[str] = None):
        """
        Args:
            midi_port: 使用するMIDIポート名
        """
        self.midi_port = midi_port
        self.channel = 0  # チャンネル1 (0-indexed)
        self._midi_out: Optional[rtmidi.MidiOut] = None
        self._additional_ports: Dict[str, rtmidi.MidiOut] = {}
        self._playback_thread: Optional[threading.Thread] = None
        self._state = PlaybackState.STOPPED
        self._current_sequence: Optional[PlaybackSequence] = None
        self._start_time: float = 0.0
        self._pause_time: float = 0.0
        self._stop_event = threading.Event()

    def get_available_ports(self) -> List[str]:
        """利用可能なMIDIポートのリストを取得"""
        midi_out = rtmidi.MidiOut()
        try:
            return midi_out.get_ports()
        finally:
            midi_out.delete()

    def connect(self, port_name: Optional[str] = None) -> None:
        """
        MIDIポートに接続する
        
        Args:
            port_name: 接続するポート名（指定しない場合は最初の利用可能ポート）
            
        Raises:
            MIDIDeviceError: 接続に失敗した場合
        """
        if self._midi_out is not None:
            self.disconnect()

        self._midi_out = rtmidi.MidiOut()
        available_ports = self._midi_out.get_ports()

        if not available_ports:
            raise MIDIDeviceError("No MIDI output ports available")

        # ポート選択
        if port_name:
            if port_name not in available_ports:
                raise MIDIDeviceError(f"MIDI port '{port_name}' not found. Available: {available_ports}")
            port_index = available_ports.index(port_name)
            self.midi_port = port_name
        else:
            # 最初の利用可能ポートを使用
            port_index = 0
            self.midi_port = available_ports[0]

        try:
            self._midi_out.open_port(port_index)
        except Exception as e:
            raise MIDIDeviceError(f"Failed to open MIDI port: {e}")

    def connect_additional_port(self, port_name: Optional[str]) -> None:
        """追加のMIDIポートに接続する"""
        if not port_name:
            return
        if port_name == self.midi_port:
            return
        if port_name in self._additional_ports:
            return

        midi_out = rtmidi.MidiOut()
        available_ports = midi_out.get_ports()
        if port_name not in available_ports:
            midi_out.delete()
            raise MIDIDeviceError(f"MIDI port '{port_name}' not found. Available: {available_ports}")
        port_index = available_ports.index(port_name)
        try:
            midi_out.open_port(port_index)
        except Exception as e:
            midi_out.delete()
            raise MIDIDeviceError(f"Failed to open MIDI port '{port_name}': {e}")

        self._additional_ports[port_name] = midi_out

    def disconnect(self) -> None:
        """MIDIポートから切断する"""
        self.stop()
        if self._midi_out is not None:
            self._midi_out.close_port()
            self._midi_out.delete()
            self._midi_out = None
        for midi_out in self._additional_ports.values():
            try:
                midi_out.close_port()
            finally:
                midi_out.delete()
        self._additional_ports.clear()

    def is_connected(self) -> bool:
        """MIDI接続状態を確認"""
        return self._midi_out is not None and self._midi_out.is_port_open()

    def _get_output_for_port(self, port_name: Optional[str]) -> Optional[rtmidi.MidiOut]:
        if port_name is None or port_name == self.midi_port:
            return self._midi_out
        return self._additional_ports.get(port_name)

    def _send_note_on_to(self, note: int, velocity: int, port_name: Optional[str]) -> None:
        midi_out = self._get_output_for_port(port_name)
        if midi_out is None or not midi_out.is_port_open():
            raise MIDIDeviceError("MIDI device not connected")
        note_on = [0x90 + self.channel, note & 0x7F, velocity & 0x7F]
        midi_out.send_message(note_on)

    def _send_note_off_to(self, note: int, port_name: Optional[str]) -> None:
        midi_out = self._get_output_for_port(port_name)
        if midi_out is None or not midi_out.is_port_open():
            raise MIDIDeviceError("MIDI device not connected")
        note_off = [0x80 + self.channel, note & 0x7F, 0]
        midi_out.send_message(note_off)

    def send_note_on(self, note: int, velocity: int = 127) -> None:
        """
        ノートオンメッセージを送信

        Args:
            note: MIDIノートナンバー (0-127)
            velocity: ベロシティ (0-127)
            
        Raises:
            MIDIDeviceError: MIDI接続がない場合
        """
        self._send_note_on_to(note, velocity, None)

    def send_note_off(self, note: int) -> None:
        """
        ノートオフメッセージを送信
        
        Args:
            note: MIDIノートナンバー (0-127)
            
        Raises:
            MIDIDeviceError: MIDI接続がない場合
        """
        self._send_note_off_to(note, None)

    def press_button(self, note: int, duration_ms: int = 50) -> None:
        """
        ボタン押下をシミュレート（ノートオン→待機→ノートオフ）
        
        Args:
            note: MIDIノートナンバー
            duration_ms: 押下時間（ミリ秒）
        """
        self.send_note_on(note)
        time.sleep(duration_ms / 1000.0)
        self.send_note_off(note)

    def play_sequence(self, sequence: PlaybackSequence) -> None:
        """
        シーケンスの演奏を開始
        
        Args:
            sequence: 演奏するシーケンス
            
        Raises:
            MIDIDeviceError: MIDI接続がない場合、または既に演奏中の場合
        """
        if not self.is_connected():
            raise MIDIDeviceError("MIDI device not connected")

        if self._state == PlaybackState.PLAYING:
            raise MIDIDeviceError("Already playing. Stop current playback first.")

        self._current_sequence = sequence
        self._state = PlaybackState.PLAYING
        self._start_time = time.time()
        self._stop_event.clear()

        # 演奏スレッドを開始
        self._playback_thread = threading.Thread(target=self._playback_worker)
        self._playback_thread.daemon = True
        self._playback_thread.start()

    def pause(self) -> None:
        """演奏を一時停止"""
        if self._state == PlaybackState.PLAYING:
            self._state = PlaybackState.PAUSED
            self._pause_time = time.time()

    def resume(self) -> None:
        """演奏を再開"""
        if self._state == PlaybackState.PAUSED:
            # 一時停止していた時間分だけ開始時刻を調整
            pause_duration = time.time() - self._pause_time
            self._start_time += pause_duration
            self._state = PlaybackState.PLAYING

    def stop(self) -> None:
        """演奏を停止"""
        if self._state != PlaybackState.STOPPED:
            self._state = PlaybackState.STOPPED
            self._stop_event.set()
            
            if self._playback_thread and self._playback_thread.is_alive():
                self._playback_thread.join(timeout=1.0)

            # 全ノートオフ
            self._send_all_notes_off()

    def get_state(self) -> PlaybackState:
        """現在の演奏状態を取得"""
        return self._state

    def get_current_time(self) -> float:
        """現在の演奏時刻を取得（秒）"""
        if self._state == PlaybackState.STOPPED:
            return 0.0
        elif self._state == PlaybackState.PAUSED:
            return self._pause_time - self._start_time
        else:
            return time.time() - self._start_time

    def _playback_worker(self) -> None:
        """演奏ワーカースレッド"""
        if not self._current_sequence:
            return

        event_index = 0
        events = self._current_sequence.events

        while (event_index < len(events) and 
               not self._stop_event.is_set() and 
               self._state != PlaybackState.STOPPED):

            # 一時停止中は待機
            if self._state == PlaybackState.PAUSED:
                time.sleep(0.01)
                continue

            event = events[event_index]
            current_time = self.get_current_time()

            # イベントの時刻になったら実行
            if current_time >= event.timestamp:
                try:
                    self._execute_event(event)
                except Exception as e:
                    print(f"Error executing MIDI event: {e}")
                
                event_index += 1
            else:
                # 少し待機してから再チェック
                time.sleep(0.001)

        # 演奏完了
        self._state = PlaybackState.STOPPED

    def _execute_event(self, event: MIDIEvent) -> None:
        """MIDIイベントを実行"""
        target_port = event.port_override
        if event.event_type == MIDIEventType.NOTE_ON:
            self._send_note_on_to(event.note, event.velocity, target_port)
        elif event.event_type == MIDIEventType.NOTE_OFF:
            self._send_note_off_to(event.note, target_port)
        elif event.event_type == MIDIEventType.SLOT_PRESS:
            # スロット選択は短時間の押下
            duration_ms = int(event.duration * 1000) if event.duration else 50
            if target_port and target_port != self.midi_port:
                self._send_note_on_to(event.note, event.velocity, target_port)
                time.sleep(duration_ms / 1000.0)
                self._send_note_off_to(event.note, target_port)
            else:
                self.press_button(event.note, duration_ms)

    def _send_all_notes_off(self) -> None:
        """全ノートオフメッセージを送信"""
        targets = [None]
        targets.extend(self._additional_ports.keys())

        for note in range(128):
            for port_name in targets:
                try:
                    self._send_note_off_to(note, port_name)
                except Exception:
                    pass  # エラーは無視

    def __del__(self):
        """デストラクタ"""
        self.disconnect()
