# 目的

「かんぷれ」というガジェットをコントロールするための Python スクリプトです。

# 処理

- json 形式でデータを受け取ってそれを変換して MIDI インターフェースから MIDI を出力します。
- 出力 MIDI インターフェースは選択できるようにします。

# json ファイル例

```
{
  "slot": 1,
  "tempo": 120,
  "notes": [
    {
      "degree": 1,
      "modifier1": 0,
      "modifier2": 0,
      "modifier3": 0
    },
    {
      "degree": 3,
      "modifier1": 1,
      "modifier2": 0,
      "modifier3": 0
    },
    {
      "degree": 5,
      "modifier1": 0,
      "modifier2": 1,
      "modifier3": 1
    },
    {
      "degree": 1,
      "modifier1": 0,
      "modifier2": 0,
      "modifier3": 0
    }
  ]
}
```

# json ファイルの解釈

MIDI.json を参照

- slot:1-8 の数字。それを配列の番号に置き換える。
- degree:1,2b,2,3b,4,5b,5,6b,6,7b,7 の文字列。それを配列の番号に置き換える。
- modifier1,modifier2,modifier3:0-8 の数字。0 はなにもしない。1-8 を配列の番号に置き換える。

# 演奏

-　各パラメーターはボタンに対応しています。MIDI ノートオン/オフを使ってボタンを押す、離すをコントロールします。

- slot の数字を MIDI note on のノートナンバーとして選択した MIDI インターフェースの ch1 で送信します。50msec で同じノートナンバーのノートオフを送信します。
- degree と modifier1,2,3 は組み合わせて送信します。modifier1,2,3 のボタンを押しながら digree のボタンを押してから離します。離した後、modifier のボタンも離します。
- tempo は BPM を表します。degree のボタンを 8 回押したら次の notes に進みます。最後まで読み終わったら終了です。
