from __future__ import annotations

import glob
import os.path as osp
from abc import ABCMeta
from typing import Union

import PySimpleGUI as sg


class AppBase(metaclass=ABCMeta):
    def __init__(
    self,
    theme: str = "Default 1",
    ) -> None:
        sg.theme(theme)
        self.error_message = ""
        # ハンドラで共有するデータを保持する辞書
        self.shared_data = dict()

    def popup_error(self, error_message='', callback=None):
        if callback is None:
            self.popup_error_hook()
        else:
            callback()
        sg.popup_error(error_message)

    def popup_error_hook(self):
        pass

    def __getitem__(self, key):
        return self.shared_data.get(key, None)

    def __setitem__(self, key, value):
        self.shared_data[key] = value

    def __delitem__(self, key):
        del self.shared_data[key]

    def ask_save_file_path(self, message) -> str:
        while True:
            path = sg.popup_get_file(message, save_as=True)
            if path is None:
                return
            if self.not_exists(osp.dirname(path)):
                sg.popup_error('フォルダが存在しません')
                continue
            break
        return path

    def ask_save_folder_path(self, message) -> str:
        while True:
            path = sg.popup_get_folder(message)
            if path is None:
                return
            if not osp.exists(path):
                sg.popup_error('フォルダが存在しません')
                continue
            break
        return path

    # --------- (以下はエラーチェック用のメソッド群) --------- #
    def is_int(self, value: str) -> bool:
        '''intに変換可能か調べる。厳密にintかどうか評価しないため注意'''
        return self.__can_convert(value, int)

    def is_not_int(self, value: str) -> bool:
        '''intに変換可能か調べる。厳密にintかどうか評価しないため注意'''
        return not self.__can_convert(value, int)

    def is_float(self, value: str) -> bool:
        '''floatに変換可能か調べる。厳密にintかどうか評価しないため注意'''
        return self.__can_convert(value, float)

    def is_not_float(self, value: str) -> bool:
        '''floatに変換可能か調べる。厳密にintかどうか評価しないため注意'''
        return not self.__can_convert(value, float)

    def is_negative(self, value: Union[int, float]) -> bool:
        '''負の値か調べる。数値の入力を想定'''
        return value < 0

    def is_positive(self, value: Union[int, float]) -> bool:
        return value > 0

    def extension_is(self, extension, s):
        return osp.splitext(s)[1] == extension

    def extension_is_not(self, extension, s):
        return osp.splitext(s)[1] != extension

    def is_not_empty_folder(self, folder_path):
        return not self.__is_empty(folder_path)

    def is_empty_folder(self, folder_path):
        return self.__is_empty(folder_path)

    def __is_empty(self, folder_path: str) -> bool:
        return len(glob.glob(osp.join(folder_path, "*"))) == 0

    def __can_convert(self, x, func):
        try:
            assert callable(func)
            func(x)
            return True
        except ValueError:
            return False

    def not_exists(self, path):
        if isinstance(path, str):
            return not osp.exists(path)
        elif isinstance(path, list):
            exist_sum = sum([osp.exists(p) for p in path if p is not None])
            return exist_sum > 0
        else:
            assert False, TypeError('ファイルの存在判定では文字列かそのリストを入力してください')

    def have(self, key, dtype=None):
        '''
        shared data内に指定されたkeyに対応するオブジェクトが存在しているか判定する。
        '''
        if key not in self.shared_data.keys():
            return False
        if dtype is not None:
            return isinstance(self.shared_data[key], dtype)
        return True
