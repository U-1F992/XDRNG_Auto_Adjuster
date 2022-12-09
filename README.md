fileencoding=utf-8
# XDRNG Auto Adjuster

## 概要

Poke-Controller-Modifiedで使用するXD乱数消費自動プログラムです。

## 導入方法

1.Poke-Controller-Modified(https://github.com/Moi-poke/Poke-Controller-Modified)を導入します。2022/10/17以降のversionが必要です。
2.xddb(https://github.com/yatsuna827/xddb)をインストールします。
3.xdrngtool(https://github.com/mukai1011/xdrngtool)をダウンロードします。
4.SerialController\Commands\PythonCommands\ImageProcessingOnlyにxdrngtoolを置きます。
5.SerialController\Commands\PythonCommands\ImageProcessingOnlyにXDRNG_Auto_Adjuster.pyを置きます。
6.SerialController\Commands\PythonCommands\ImageProcessingOnly\xdrngtoolにある__init__.pyを本リポジトリのものに置き換えます。
7.SerialController\TemplateにXDRNGのディレクトリを作成し、以下のリンクにある画像ファイルをすべて入れてください。これらのファイルは必要に応じて自分の環境で取得し、置き換える必要がある場合があります。
　(https://drive.google.com/file/d/1vcYS97HPNSDmiuK-YuXq268XtlcZOhoa/view?usp=sharing)

## 使い方

1.Poke-Controller-ModifiedでPython CommandにあるXDRNG自動消費 v.x.x.xを選択し、Startをクリックします。
2.目標seed、tsv、もちもの消費を入力しokをクリックします。

### 目標seed

関数の終了時に、そのseedに合っている状態になります。強制消費は事前に調査し、差し引いたseedを入力してください。

### TSV

`None`でも構いませんが、正確に指定したほうがいいです。いますぐバトルの生成予測に齟齬が生じ、消費経路の再計算が発生する可能性があります。

ライブラリ側で対処しているため通常は問題ありませんが、運悪く消費中の最後の数回で再計算が発生すると、経路の修正が利かずまずそうです（超レアなケースなので、もし遭遇したら報告をお待ちしています）。

### もちもの消費

`advances_by_opening_items`は「もちもの」を開閉する操作にかかる消費数です。設定によって、終了時の状況が異なります。関数以降に自動操作を続ける場合は注意してください。

| 設定値     | 動作                                                                                                                                                                 |終了位置|
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |---|
| `None`     | フィールドに NPC 等不定消費要素があり、ロード後の seed 調整が不可能な場合に使用します。<br>ロードせず、振動設定の変更（40 消費）のみで seed の調整を行います。       |メニュー画面（カーソルが「せってい」に合っている状態）|
| `None`以外 | フィールドに NPC 等不定消費要素がなく、ロード後に seed 調整が可能な場合に使用します。<br>ロードを挟み、振動設定の変更とレポート（63 消費）で seed の調整を行います。 |フィールド（メニューが開き、カーソルが「レポート」に合っている状態）|

## Reference

- [xddb](https://github.com/yatsuna827/xddb)
- [xdrngtool](https://github.com/mukai1011/xdrngtool)
- [XDSeedSorter](https://github.com/mukai1011/XDSeedSorter)

## ライセンスについて

複製・再頒布：可能
改変：可能
改変部分のソース公開：不要
他のコードと組み合わせた場合他のコードのソース公開：不要
商用利用：禁止(本項目のみ、本プログラムからの派生物すべてに適用してください。)
(今後MITライセンスに変更する可能性があります。)

## 謝辞
以下のプログラム作成者の方々に御礼申し上げます。
yatsuna827(https://github.com/yatsuna827)
mukai1011(https://github.com/mukai1011)