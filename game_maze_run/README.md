# Game "Maze Run" #

MazeArena Console 的基本功能示範遊戲。探索迷宮的路徑組成，並描繪迷宮樣貌。

## 使用遊戲 ##

在 `application_gui.py` 中，將包含遊戲的 module 替換成 `game_maze_run`，
如：
```python
from game_maze_run import GameCore, GameConsoleWidget
```

## 遊戲指令 ##

**由 server 發出**

* `game-start`：遊戲開始
* `game-stop`：遊戲結束

**由玩家發出**

* `position`：請求自己在迷宮中的位置
  - server 回傳 `position <x> <y>`
* `game-touch`：完成遊戲目標

## 遊戲流程 ##

1. 確認玩家連上線並指定辨識顏色
2. 設定計時器模式 (計時或倒數)
3. 按"遊戲開始"鍵開始遊戲，server 廣播 `game-start` 訊息，並開始計時
4. 當 server 收到 `game-touch` 訊息時，停止計時，結束遊戲，並發出
   `game-stop` 訊息

其他遊戲結束的情況，視玩法而定：

* 由控制介面直接結束遊戲
* 計時器倒數結束 (如果設為倒數模式)