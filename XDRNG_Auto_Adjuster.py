#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.Keys import Button, Direction
from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.PythonCommands.ImageProcessingOnly.xdrngtool import TeamPair, execute_automation

import Settings

import datetime
import cv2
import string
import random
import numpy as np
import os
import time

import re
from PIL import Image, ImageOps
import pyocr
import pyocr.builders
pyocr.tesseract.TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 
tools = pyocr.get_available_tools()
try:
    tool = tools[0]
except:
    print("tesseract.exeが見つかりません。")

from xddb import EnemyTeam, PlayerTeam

warning0 = "XDRNG/warning.png"
nintendo = "XDRNG/nintendo.png"

opening = "XDRNG/opening.png"
name0 = "XDRNG/name.png"

Articuno = "XDRNG/Articuno.png"
Deoxys = "XDRNG/Deoxys.png"
Jirachi = "XDRNG/Jirachi.png"
Kangaskhan = "XDRNG/Kangaskhan.png"
Latias = "XDRNG/Latias.png"
Mew = "XDRNG/Mew.png"
Mewtwo = "XDRNG/Mewtwo.png"
Moltres = "XDRNG/Moltres.png"
Rayquaza = "XDRNG/Rayquaza.png"
Zapdos = "XDRNG/Zapdos.png"

stop_battle_check = "XDRNG/stop_battle_check.png"
stop_battle_active = "XDRNG/stop_battle_active.png"

vibration_active = "XDRNG/vibration_active.png"
write_memory_card = "XDRNG/write_memory_card.png"

menu_pokemon_active = "XDRNG/menu_pokemon_active.png"

class TransitionToQuickBattle():
    def __init__(self, command):
        self.__command = command
    
    def run(self):
        # SWリセットする
        self.__command.sw_reset()
        # 起動画面から移動する。
        while not self.__command.isContainTemplate(nintendo, threshold=0.9, use_gray=False, show_value=False):
            self.__command.press(Button.A, wait=0.5)
        # タイトル画面表示まで待機する。
        while not self.__command.isContainTemplate(opening, threshold=0.9, use_gray=False, show_value=False):
            self.__command.wait(0.5)
        self.__command.wait(1.0)
        self.__command.press(Button.A, wait=1.5)
        self.__command.press(Button.A, wait=1.0)
        # カーソルを対戦モードに移動する。(一度「もどる」まで動かしてから対戦モードに移動させる。)
        self.__command.press(Direction.RIGHT, duration=1.0, wait=0.5)
        self.__command.press(Direction.UP, wait=0.5)
        # いますぐバトルの生成画面まで移動する。
        self.__command.press(Button.A, wait=2.5)
        if self.__command.isContainTemplate(name0, threshold=0.9, use_gray=False, show_value=False):
            self.__command.transition_to_quick_battle()
        else:
            self.__command.press(Button.A, duration=0.07, wait=3.5)
            self.__command.press(Button.A, duration=0.07, wait=1.0)
            self.__command.press(Button.A, duration=0.07, wait=1.5)
    
    def sw_reset(self):
        # リセット
        if self.__command.cnt_reset != 0:
            print("ソフトウェアリセット実行(%d回目)" % (self.__command.cnt_reset))
        self.__command.press([Button.A, Button.B, Button.X, Button.R, Button.L, Button.HOME], duration=1.0)
        # タイトル画面表示まで待機する
        while not self.__command.isContainTemplate(warning0, threshold=0.9, use_gray=False, show_value=False):
            self.__command.wait(0.5)
        self.__command.wait(1.0)
        # HITSUMABUSHIの内部状態初期化(ZLはマイコン内部を初期化する処理の実行トリガー)
        self.__command.press(Button.ZL, wait=1.0)
        # COMポートリロード
        self.__command.reload_com_port()
        self.__command.wait(1.0)
        # カウンタ
        self.__command.cnt_reset += 1
        self.__command.cnt_quick_battle = 0

class GenerateNextTeamPair():
    def __init__(self, command):
        self.__command = command
    
    def quick_battle_check_pokemon(self):
        def image_pre_processing(image, threshold = 170, mode="dark"):
            img = image
            #グレースケール化
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            #閾値処理
            img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)[1]
            #反転
            if mode == "dark":
                img = cv2.bitwise_not(img)
            return img
        
        def ocr(img, th, left, top, right, down, tesseract_layout_value, mode=0):
            img = image_pre_processing(img, threshold = th, mode="dark")
            img = Image.fromarray(img)
            image_crop = img.crop((left, top, right, down))
            w, h = image_crop.size
            image_crop = image_crop.resize((int(w*4.0/1.22), h*4))
            # image_crop.show()
            if mode == 1:
                hp0=""
                for i in range(3):
                    image_crop_1 = image_crop.crop((i*(int(w*4.0/1.22))//3, 0, (i+1)*(int(w*4.0/1.22))//3, h*4))
                    # image_crop_1.show()
                    hp1 = tool.image_to_string(image_crop_1, builder=pyocr.builders.DigitBuilder(tesseract_layout=tesseract_layout_value))
                    hp0 = hp0 + hp1
            else:
                hp0 = tool.image_to_string(image_crop, builder=pyocr.builders.DigitBuilder(tesseract_layout=tesseract_layout_value))
            return hp0

        # HPが表示されている場所
        # left top right down
        leftbox  = [265+70, 265+70, 808+70, 808+70]
        topbox   = [454, 592, 454, 592]
        rightbox = [433, 433, 976, 976]
        downbox  = [487, 625, 487, 625]
        player_png = [ Mewtwo, Mew, Deoxys, Rayquaza, Jirachi ]
        computer_png = [ Articuno, Zapdos, Moltres, Kangaskhan, Latias ]
        # 結果表示用文字列
        player = [ "Mewtwo", "Mew", "Deoxys", "Rayquaza", "Jirachi" ]
        computer = [ "Articuno", "Zapdos", "Moltres", "Kangaskhan", "Latias" ]
        tesseract_layout_value = 6
        img = self.__command.camera.readFrame()
        
        result_player = None
        index, _, _ = self.__command.isContainTemplate_max(player_png, threshold=0.75, use_gray=False, show_value=False)
        if index == 0:
            result_player = PlayerTeam.Mewtwo
        elif index == 1:
            result_player = PlayerTeam.Mew
        elif index == 2:
            result_player = PlayerTeam.Deoxys
        elif index == 3:
            result_player = PlayerTeam.Rayquaza
        elif index == 4:
            result_player = PlayerTeam.Jirachi
        else:
            pass
        if self.__command.result_ocr_show == True:
            print("1P :", player[index])

        result_computer = None
        index, _, _ = self.__command.isContainTemplate_max(computer_png, threshold=0.75, use_gray=False, show_value=False)
        if index == 0:
            result_computer = EnemyTeam.Articuno
        elif index == 1:
            result_computer = EnemyTeam.Zapdos
        elif index == 2:
            result_computer = EnemyTeam.Moltres
        elif index == 3:
            result_computer = EnemyTeam.Kangaskhan
        elif index == 4:
            result_computer = EnemyTeam.Latias
        else:
            pass
        if self.__command.result_ocr_show == True:
            print("COM:", computer[index])

        result_hp = []
        cnt = 0
        for left, top, right, down in zip(leftbox, topbox, rightbox, downbox):
            cnt0 = 0
            while True:
                cnt0 += 1
                hp0 = ocr(img, 170, left, top, right, down, tesseract_layout_value)
                hp = re.sub(r"\D", "", hp0)
                if self.__command.result_ocr_show == True:
                    print("HP",cnt,":",hp, len(hp))
                if len(hp) != 3:
                    if self.__command.result_ocr_show == True:
                        print("retry")
                    hp0 = ocr(img, 170, left, top, right, down, 10, mode=1)
                    hp = re.sub(r"\D", "", hp0)
                    if self.__command.result_ocr_show == True:
                        print("HP(retry)",cnt,":",hp, len(hp))
                if len(hp) != 3 and cnt0 <= 5:
                    if self.__command.result_ocr_show == True:
                        print("reload image")
                    img = self.__command.camera.readFrame()
                else:
                    break
            result_hp.append(int(hp))
            cnt += 1
        # ずっと操作をしていると入力を受け付けなくなるため、ポートの初期化をする。
        if self.__command.cnt_quick_battle % 30 == 29:
            print("30回判定したのでポートをリロードします。(%d回目)" % (self.__command.cnt_quick_battle//30+1) )
            if self.__command.cnt_quick_battle == 29 and self.__command.result_ocr_show == True:
                print("処理高速化のためにOCR結果表示をOFFにします。")
                self.__command.result_ocr_show == False
            # HITSUMABUSHIの内部状態初期化(ZLはマイコン内部を初期化する処理の実行トリガー)
            self.__command.press(Button.ZL, wait=1.0)
            # COMポートリロード
            self.__command.reload_com_port()
            self.__command.wait(1.0)
        self.__command.cnt_quick_battle += 1
        return (result_player, result_hp[0], result_hp[1]), (result_computer, result_hp[2], result_hp[3])    

    def run(self) -> TeamPair:
        # いますぐバトルを一旦閉じていますぐバトルの生成画面まで移動する。
        self.__command.press(Button.B, wait=0.5)
        self.__command.press(Button.A, wait=1.0)
        # 1PとCOMの個体/HPを読み取る。
        player , computer = self.__command.quick_battle_check_pokemon()
        
        return (player, computer)

class EnterWaitAndExitQuickBattle():
    def __init__(self, command):
        self.__command = command

    def run(self, td):
        # 「はい」を押す
        self.__command.press(Button.A)
        # 待機する
        self.__command.wait(td)        
        # 降参する。
        self.__command.press(Button.HOME, wait=0.1)
        self.__command.press(Direction.DOWN, wait=0.1)       
        self.__command.press(Button.A, wait=0.1)
        # 選択画面まで待機する。
        while not self.__command.isContainTemplate(stop_battle_check, threshold=0.9, use_gray=False, show_value=False):
            self.__command.wait(0.5)
        self.__command.wait(0.5)
        self.__command.press(Direction.DOWN, wait=0.5)
        # 対戦をやめていますぐバトルの生成画面まで移動する。
        self.__command.press(Button.A, wait=2.0)
        self.__command.press(Button.A, wait=0.5)
        self.__command.wait(1.0)
        # HITSUMABUSHIの内部状態初期化(ZLはマイコン内部を初期化する処理の実行トリガー)
        self.__command.press(Button.ZL, wait=1.0)
        # COMポートリロード
        self.__command.reload_com_port()
        self.__command.wait(1.0)

class SetCursorToSetting():
    def __init__(self, command):
        self.__command = command
    
    def run(self):
        # タイトル画面まで移動する。
        self.__command.press(Button.B, wait=0.5)
        self.__command.press(Button.B, wait=0.5)
        self.__command.press(Button.B, wait=1.0)
        self.__command.press(Button.B, wait=1.0)
        # カーソルを対戦モードに移動する。(一度「もどる」まで動かしてから対戦モードに移動させる。)
        self.__command.press(Direction.RIGHT, duration=1.0, wait=0.5)
        self.__command.press(Direction.LEFT, wait=0.5)

class ChangeSetting():
    def __init__(self, command):
        self.__command = command
    
    def run(self):
        # 設定画面に移動してしんどうにカーソルを合わせる。
        self.__command.press(Button.A, wait=1.2)
        self.__command.press(Direction.DOWN, wait=0.5)
        # 現在の設定を確認する。「あり」になっている場合右、「なし」になっている場合左を押す。
        for i in range(6):
            if self.__command.isContainTemplate(vibration_active, threshold=0.85, use_gray=True, show_value=False):
                self.__command.press(Direction.RIGHT, wait=0.5)
                i -= 1
                break
        if i == 5:
            self.__command.press(Direction.LEFT, wait=0.5)
        # 「おわる」を押して設定を保存する。
        self.__command.press(Direction.DOWN, wait=0.5)
        self.__command.press(Button.A, wait=0.5)
        self.__command.press(Direction.UP, wait=0.5)
        self.__command.press(Button.A, wait=0.5)
        # メモリーカードに書き込まれるまで待機する。
        while self.__command.isContainTemplate(write_memory_card, threshold=0.85, use_gray=True, show_value=False):
            self.__command.wait(0.5)
        self.__command.wait(0.5)
        # タイトル画面に戻る
        self.__command.press(Button.A, wait=1.0)

class Load():
    def __init__(self, command):
        self.__command = command
    
    def run(self):
        # カーソルを「つづきから」に移動して選択する。
        self.__command.press(Direction.UP, wait=0.5)
        self.__command.press(Button.A, wait=1.5)
        # カーソルを「はい」に移動する。
        self.__command.press(Direction.UP, wait=0.8)
        self.__command.press(Button.A, wait=0.5)
        # メニューが開くまでXを連打する。
        while not self.__command.isContainTemplate(menu_pokemon_active, threshold=0.85, use_gray=False, show_value=False):
            self.__command.press(Button.X)
        # カーソルを「レポート」に移動する。
        for i in range(3):
            self.__command.press(Direction.DOWN, wait=0.3)

class WriteReport():
    def __init__(self, command):
        self.__command = command

    def run(self):
        # セーブする。
        self.__command.press(Button.A, wait=0.5)
        self.__command.press(Button.A, wait=0.5)
        self.__command.press(Direction.UP, wait=0.5)
        self.__command.press(Button.A, wait=1.0)
        # メモリーカードに書き込まれるまで待機する。
        while self.__command.isContainTemplate(write_memory_card, threshold=0.85, use_gray=True, show_value=False):
            self.__command.wait(0.5)
        self.__command.wait(0.3)
        # メニュー画面に戻る。
        self.__command.press(Button.A, wait=0.5)

class xd_rng_auto_adjuster(ImageProcPythonCommand):
    NAME = 'XDRNG自動消費 v.0.0.2'

    def __init__(self, cam, gui=None):
        super().__init__(cam)
        self.cnt_reset = 0
        self.cnt_quick_battle = 0
        self.result_ocr_show = False

    def config(self, default_tsv):
        
        ret = self.dialogue("config", ["目標seed(複数の場合は(,)で区切ってください)", "tsv(指定しない場合、いますぐバトルの生成結果に齟齬が生じ再計算が発生する可能性があります)", "もちものを開く際の消費数"])
        
        self.target_seeds = []        
        self.config_check = True
        
        try:
            if ret[0] != "":
                for seed in ret[0].split(","):
                    self.target_seeds.append(int(seed, 16))
        except:
            print("TARGET SEEDS: ERROR")
            return False
        
        try:
            if ret[1] != "":
                self.tsv = int(ret[1], 16)
                print("USE TSV: %s" % (self.tsv))
            else:
                self.tsv = default_tsv
                if self.tsv == 0:
                    print("USE TSV: %s(DEFAULT)" % (self.tsv))
        except:
            print("TSV: ERROR")
            return False
        
        try:
            if ret[2] != "":
                self.advances_by_opening_items = int(ret[2])
                print("OPTION: %d" % (self.advances_by_opening_item))
            else:
                self.advances_by_opening_items = None
                print("OPTION: None")
        except:
            print("OPTION: Error")
            return False

        return True

    def do(self):
        print("-------------------------------------")
        print("XDRNG自動消費 v.0.0.2")
        print("Developed by.夜綱様,メイユール様,フウ")
        print("-------------------------------------")

        USER_TSV = 2412 #xdrngtool.DEFAULT_TSV
        result = self.config(default_tsv = USER_TSV)
        
        TransitionToQuickBattle     = TransitionToQuickBattle(self)
        GenerateNextTeamPair        = GenerateNextTeamPair(self)
        EnterWaitAndExitQuickBattle = EnterWaitAndExitQuickBattle(self)
        SetCursorToSetting          = SetCursorToSetting(self)
        ChangeSetting               = ChangeSetting(self)
        Load                        = Load(self)
        WriteReport                 = WriteReport(self)

        operations = (
                    TransitionToQuickBattle(),
                    GenerateNextTeamPair(),
                    EnterWaitAndExitQuickBattle(),
                    SetCursorToSetting(),
                    ChangeSetting(),
                    Load(),
                    WriteReport(),
                )

        execute_automation(operations, self.target_seeds, self.tsv, self.advances_by_opening_items)

        self.finish()   
    