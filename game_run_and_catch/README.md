# Game "Run and Catch" #

�ݥѨ��i�檺�C���A�@���t�k�`�� (Runner)�A�t�@���t�l�v�� (Catcher)�A
�k�`�̥����b�ɭ������Q�l�v�̧��A�άO�F�����w���ؼСC
�l�v�̫h�����b�k�`�̧����ؼЫe���Ҧ��k�`�̡C

## �ϥιC�� ##

�b `application_gui.py` ���A�N�]�t�C���� module ������ `game_run_and_catch`�A
�p�G
```python
from game_run_and_catch import GameCore, GameConsoleWidget
```

## �g�c�y�z ##

�t�ΧP�w�ݭn�g�c���˻��A�� [`maze_map.txt`](maze_map.txt) �w�q�һݪ���T�A
�m��P�C���P�@�Ӹ�Ƨ��U�C�C�@��O���@��g�c���۳q���Y�A
���Ǭ� row-major (row 2, col 1 �w�q���O�y�� (1, 2) ����l�A�g�c���U���� (0, 0))�C
�榡���G

* `#`�G���ѡA�H # �}�Y���Ӧ��r���|�QŪ�J
* `0b1111`�G�w�q�C�Ӱg�c��l�P�|�Ӭ۾F��l���s�����Y�C
  �ϥ� 4 �� bit �ӥN���� (bit 3)�B�U�� (bit 2)�B�k�� (bit 1)�B�W�� (bit 0)�A
  �p�G�Ӯ�P�o��g�c�۳q�h�� bit �Ȭ� 1�A�_�h�� 0�C
  �Ҧp�G�p�G�Ӯ�P�W�U���۳q�A���k��榳��j�}�A��Ȭ� `0b0101`�C

## �C�����O ##

**�� server �o�X**
* `game-start`�G�C���}�l
* `game-stop`�G�C������
* `game-catched`�G(�u���k�`��~�|����)�A�Q�P�w�Q�l�v����

**�Ѫ��a�o�X**

* `position`�G���o�ۤv�b�g�c������m�Aserver �^�� `position <x> <y>`
* `position-team`�G���o���� (�]�A�ۤv) �b�g�c������m
  + server �^�� `position-team [<ID> <x> <y>]+`�A
   �Ҧp�G`position-team Bob 2 3 Alice 3 5`
* `position-enemy`�G���o�Ĥ�b�g�c������m
  + server �^�� `position-enemy [<x> <y>]+`�A�Ҧp�G`position-enemy 1 2 0 3`
* `game-touch`�G(�u���k�`��o�X����)�A�������w���ؼ�

## �C���y�{ ##

1. �T�{���w�g�s�W�C���A�ë��w�n�����������C��
2. �]�w�p�ɾ��Ҧ� (�p�ɩέ˼�)
3. ��"�C���}�l"��}�l�C���Aserver �s�� `game-start` �T���A�ö}�l�p��
4. Server ����P�w�k�`�̬O�_�Q�l�v�̧��A�p�G���h�o�X `game-catched` �T�����k�`��
5. �ˬd���W�O�_�٦��s�����l�v�̡A�p�G�S���h�����C���A�o�X `game-stop` �T���A�p�ɰ���

��L�C�����������p�A�����k�өw�G

* �ѱ�������������C��
* �k�`�觹���ؼ�
* �p�ɾ��˼Ƶ��� (�p�G�]���˼ƼҦ�����)

## �C������ ##

![](./img/run_and_catch.PNG "�C������")

�p�G�Ӱk�`���٦s���A���C����Ҭ�����A�_�h���Ǧ�