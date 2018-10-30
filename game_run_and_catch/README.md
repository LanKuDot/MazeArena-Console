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