# MazeArena Console #

迷宮車遊戲 MazeArena 的車子位置辨識程式 (使用 OpenCV)，
同時作為遊戲的伺服器 (使用 TCP Server) 與遊戲事件的主控台。

MazeArena 是由一個迷宮場地與數台迷宮車組成的場景。
迷宮車具有通訊能力，用來與伺服器溝通或是透過伺服器與其他迷宮車溝通，
同時帶有一個 RGB LED 燈，用來讓車輛辨識程式辨別車輛在迷宮中的位置。

## 需求 ##

**額外設備**

* 無線 AP 作為連線之用
* USB 攝影機

**Python 需求與套件**

* Python 3.6 以上
* colorama
* colors.py
* imutils
* numpy
* opencv-python

套件使用版本可參考 [`requirements.txt`](requirements.txt)

## 操作流程 ##

[Youtube 影片](https://youtu.be/mDIv9mxErNQ)，記得開 CC 字幕

## 遊戲 ##

* [**Maze Run**](game_maze_run/README.md)：
  MazeArena Console 的基本功能示範遊戲。迷宮車透過請求自己的位置來描繪迷宮樣貌。
* [**Run and Catch**](game_run_and_catch/README.md)：
  由兩隊組成，一方扮演逃亡者 (Runner)，一方則扮演追逐者 (Catcher)。
  逃亡方在全員被抓起來前完成指定的目標。

## 基本伺服器指令 ##

在遊戲中，迷宮車必須透過指令與伺服器溝通

* `join <ID> <team>`：加入遊戲
  - `ID`：迷宮車的識別名稱
  - `team`：要加入隊伍的名稱
  - 伺服器回應：`join ok` 或 `join fail`
* `send-to <ID> <message>`：傳訊息給指定 ID 的迷宮車，只有同隊才有效
  - `ID`：同隊的迷宮車 ID
  - `message`：要傳遞的訊息
  - 伺服器回應：`send-to ok`
  - 隊友收到的訊息格式：`send-from <ID> <message>`
    - `ID`：訊息來源 ID
    - `message`：收到的訊息
* `send-team <message>`：傳訊息給所有隊友
  - `message`：要傳遞的訊息
  - 伺服器回應：`send-team ok`
  - 隊友收到的訊息同 `send-to` 指令

若要離開遊戲，直接離開 TCP server 即可。

## 設定額外參數 ##

部分參數需透過修改程式碼來設定，皆在 [`application_gui.py`](application_gui.py)

**設定 USB 攝影機**

```python
_camera = WebCamera(src = 0, width = 1080, height = 720)
```

* `src`：USB 攝影機的 ID，通常是插入電腦的順序。筆電 Webcam 通常是 0，
  因此再插入新的 USB 攝影機，其 ID 為 1
* `width` 及 `height`：攝影機的影像解析度，為該攝影機可支援的解析度

**設定位置更新頻率**

程式的 CPU 使用率大部分來自計算位置的更新頻率，
考量到迷宮車的移動速度與請求位置的速率，設定為合適的值，以降低程式的 CPU 使用率。
頻率過高可讓程式的 CPU 使用率達 100%。

```python
_color_pos_manager = ColorPosManager(_camera, fps = 50)
_maze_manager = MazeManager(_color_pos_manager, fps = 50)
```

* `fps`：位置的更新頻率
