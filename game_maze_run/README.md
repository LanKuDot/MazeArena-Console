# Game "Maze Run" #

MazeArena Console ���򥻥\��ܽd�C���C�����g�c�����|�զ��A�ôyø�g�c�˻��C

## �ϥιC�� ##

�b `application_gui.py` ���A�N�]�t�C���� module ������ `game_maze_run`�A
�p�G
```python
from game_maze_run import GameCore, GameConsoleWidget
```

## �C�����O ##

**�� server �o�X**

* `game-start`�G�C���}�l
* `game-stop`�G�C������

**�Ѫ��a�o�X**

* `position`�G�ШD�ۤv�b�g�c������m
  - server �^�� `position <x> <y>`
* `game-touch`�G�����C���ؼ�

## �C���y�{ ##

1. �T�{���a�s�W�u�ë��w�����C��
2. �]�w�p�ɾ��Ҧ� (�p�ɩέ˼�)
3. ��"�C���}�l"��}�l�C���Aserver �s�� `game-start` �T���A�ö}�l�p��
4. �� server ���� `game-touch` �T���ɡA����p�ɡA�����C���A�õo�X
   `game-stop` �T��

��L�C�����������p�A�����k�өw�G

* �ѱ�������������C��
* �p�ɾ��˼Ƶ��� (�p�G�]���˼ƼҦ�)