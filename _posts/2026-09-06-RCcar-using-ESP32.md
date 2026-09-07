---
title: ESP32でラジコンを作ったメモ
---

## はじめに

参考文献[[1](https://ameblo.jp/kenjii70/entry-12879925965.html)]を参考にしながら、ESP32でラジコンを作る。ほとんど参考文献のとおり＆AIフル活用です……。

## できたもの

外観はこんな感じ。前輪は100均で買った家具用キャスターを利用している。

{% include image.html file="esp32_car.JPG" alt="ラジコン" %}

家に転がっていたPS4のコントローラーで動くようにした。

<video src="{{ '/assets/static/esp32_car.mp4' | relative_url }}" controls></video>

## 使ったもの

### ESP32互換ボード

{% include amazon_card.html url="https://amzn.to/4doQTnY" title="ELEGOO ESP-32-開発ボード Micro USB 2.4GHz デュアルモード CP2102チップ 2個セット" brand="ELEGOO" %}

ESP32はWi-FiとBluetoothが載ったArduino互換のマイコン。ゲームコントローラーとも無線でつなげる。

様々な開発ボードがある。よく確認せず買ったため、到着後にMicroUSBだったことに気づいた。USB-Cで通信できるボードのほうが使い勝手がいいはず。

### モータードライバ

{% include amazon_card.html url="https://amzn.to/3VgKDsb" title="L298N モータードライブコントローラーボード" %}

ESP32からの微小な信号（3.3V）を受けて、単3電池x4（6V）から供給される電流をスイッチングし、モーターへ流す役割。

### タイヤ＋ギヤードモーター

{% include amazon_card.html url="https://amzn.to/46HyaAh" title="TTモーターホイールキット 4個セット DC3-12V 1A" %}

DCモーターにギヤがついたセット。4つ入り。

### ブレッドボード

{% include amazon_card.html url="https://amzn.to/4gSvyUW" title="サンハヤト ニューブレッドボード SAD-101" brand="サンハヤト" %}

通常のブレッドボードだとESP32基板を挿し込むと、片側に空きがない。SAD-101だと、両側に空きができる。こちらのブログ[[2](https://spiceman.jp/esp32-recommendation/)]を参考にした。

↓ 通常のブレッドボード。右側に空きがない。

{% include image.html file="esp32_board_conventional.JPG" alt="通常のブレッドボード" %}

↓ SAD-101の場合、空きができる。

{% include image.html file="esp32_board_new.JPG" alt="SAD-101" %}

### 電池ボックス

{% include amazon_card.html url="https://amzn.to/4cwQ1NN" title="Kaito Denshi 電池ボックス 単3 乾電池 4本 BH341-2A" brand="海渡電子" %}

### プラダン

ダイソーで購入。

{% include link_card.html url="https://jp.daisonet.com/products/4549131967128" %}

### キャスター

ダイソーで購入。

{% include link_card.html url="https://jp.daisonet.com/products/4549131304015" %}

### USB-C to 5V基板

自作。JLCPCBの使い方練習のため作ったやつ。USB-Cから5Vを取り出し、ブレッドボードに供給するだけの基板。

{% include image.html file="usbc-to-5v.JPG" alt="usbc-to-5v" %}

### モバイルバッテリー

普段使いのモバイルバッテリーを利用。ESP-32基板に5Vを供給するために利用。

{% include amazon_card.html url="https://amzn.to/4dhpW5x" title="モバイルバッテリー" %}

## 作る

AIフル活用のVibe工作。

以下の通りにモータードライバーとESP32を接続する。

```
 HW-095          ESP32
 ENA (左PWM)  -> GPIO14
 IN1          -> GPIO26
 IN2          -> GPIO27
 ENB (右PWM)  -> GPIO32
 IN3          -> GPIO25
 IN4          -> GPIO33
 GND          -> GND (共通必須)
 +12V(モータ電源) -> モーター用電源 (6-12V推奨)
```

{% include image.html file="motor-driver.JPG" alt="モータードライバー" %}

モータードライバーの左右端子はモーター、画面左下の端子は電池、右下はESP32に接続。

### コーディング

エージェントフル活用。コードはこちらから。

{% include github_card.html url="https://github.com/mhr380/esp32-rccar" %}

### PS4コントローラーとの接続

PS4コントローラーは最後に接続した機器のMACアドレスを覚えており、コントローラー起動時は自動でその機器を探してしまう。これを避けるために、ESP32のMACアドレスを取得し、PS4コントローラーに書き込む必要がある。

上記コードをUSBでPCに接続しながら実行し、シリアルを確認すると、ESP32のMACアドレスを表示するようにしている。

```
ESP32 PS4 Motor Control
ESP32 BT MAC: XX:XX:XX:XX:XX:XX
PS4 connected
```

PS4コントローラーのMACアドレスを上書きするために、SixaxisPairToolを利用する。以下からダウンロードし、インストールする。

[https://sixaxispairtool.en.lo4d.com/download](https://sixaxispairtool.en.lo4d.com/download)

インストール完了後、USBケーブルでPS4コントローラーをPCに接続し、Change Master欄に、上記のMACアドレスを入力してUpdateを押下する。中央のPSボタンを押すと青に点滅するが、ESP32と接続すると、緑になる。

{% include image.html file="sixaxisPairTool.jpg" alt="SixaxisPairTool" %}

ここまで行うと、コントローラーでラジコン操作が実行できる。

## 参考文献

[1] [ESP32でBluetoothラジコンカーを作ってみた](https://ameblo.jp/kenjii70/entry-12879925965.html)

[2] [電子工作初心者におすすめのESP32開発ボードはどれ？](https://spiceman.jp/esp32-recommendation/)
