# MazeArena Console #

�g�c���C�� MazeArena �����l��m���ѵ{�� (�ϥ� OpenCV)�A
�P�ɧ@���C�������A�� (�ϥ� TCP Server) �P�C���ƥ󪺥D���x�C

MazeArena �O�Ѥ@�Ӱg�c���a�P�ƥx�g�c���զ��������C
�g�c���㦳�q�T��O�A�ΨӻP���A�����q�άO�z�L���A���P��L�g�c�����q�A
�P�ɱa���@�� RGB LED �O�A�Ψ����������ѵ{����O�����b�g�c������m�C

## �ݨD ##

**�B�~�]��**

* �L�u AP �@���s�u����
* USB ��v��

**Python �ݨD�P�M��**

* Python 3.6 �H�W
* colorama
* colors.py
* imutils
* numpy
* opencv-python

�M��ϥΪ����i�Ѧ� [`requirements.txt`](requirements.txt)

## �ާ@�y�{ ##

[Youtube �v��](https://youtu.be/mDIv9mxErNQ)�A�O�o�} CC �r��

## �C�� ##

* [**Maze Run**](game_maze_run/README.md)�G
  MazeArena Console ���򥻥\��ܽd�C���C�g�c���z�L�ШD�ۤv����m�Ӵyø�g�c�˻��C
* [**Run and Catch**](game_run_and_catch/README.md)�G
  �Ѩⶤ�զ��A�@���t�k�`�� (Runner)�A�@��h��t�l�v�� (Catcher)�C
  �k�`��b�����Q��_�ӫe�������w���ؼСC

## �򥻦��A�����O ##

�b�C�����A�g�c�������z�L���O�P���A�����q

* `join <ID> <team>`�G�[�J�C��
  - `ID`�G�g�c�����ѧO�W��
  - `team`�G�n�[�J����W��
  - ���A���^���G`join ok` �� `join fail`
* `send-to <ID> <message>`�G�ǰT�������w ID ���g�c���A�u���P���~����
  - `ID`�G�P�����g�c�� ID
  - `message`�G�n�ǻ����T��
  - ���A���^���G`send-to ok`
  - ���ͦ��쪺�T���榡�G`send-from <ID> <message>`
    - `ID`�G�T���ӷ� ID
    - `message`�G���쪺�T��
* `send-team <message>`�G�ǰT�����Ҧ�����
  - `message`�G�n�ǻ����T��
  - ���A���^���G`send-team ok`
  - ���ͦ��쪺�T���P `send-to` ���O

�Y�n���}�C���A�������} TCP server �Y�i�C

## �]�w�B�~�Ѽ� ##

�����Ѽƻݳz�L�ק�{���X�ӳ]�w�A�Ҧb [`application_gui.py`](application_gui.py)

**�]�w USB ��v��**

```python
_camera = WebCamera(src = 0, width = 1080, height = 720)
```

* `src`�GUSB ��v���� ID�A�q�`�O���J�q�������ǡC���q Webcam �q�`�O 0�A
  �]���A���J�s�� USB ��v���A�� ID �� 1
* `width` �� `height`�G��v�����v���ѪR�סA������v���i�䴩���ѪR��

**�]�w��m��s�W�v**

�{���� CPU �ϥβv�j�����Ӧۭp���m����s�W�v�A
�Ҷq��g�c�������ʳt�׻P�ШD��m���t�v�A�]�w���X�A���ȡA�H���C�{���� CPU �ϥβv�C
�W�v�L���i���{���� CPU �ϥβv�F 100%�C

```python
_color_pos_manager = ColorPosManager(_camera, fps = 50)
_maze_manager = MazeManager(_color_pos_manager, fps = 50)
```

* `fps`�G��m����s�W�v
