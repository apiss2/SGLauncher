import glob
import os.path as osp
from abc import ABCMeta, abstractmethod
from typing import List

import PySimpleGUI as sg


class Layout(metaclass=ABCMeta):
    @abstractmethod
    def get_layout(self) -> list:
        pass

    @abstractmethod
    def get_keys(self) -> List[str]:
        pass


class Handler(metaclass=ABCMeta):
    def __init__(self, app, successor=None, event: str = None):
        self.app = app
        self.__successor = successor
        self.event = event

    @abstractmethod
    def proc(self, values):
        pass

    def handle(self, event, values):
        if event == self.event:
            self.proc(values)
        else:
            if self.__successor is not None:
                self.__successor.handle(event, values)


class App(object):
    def __init__(
        self,
        app_name: str,
        layout: Layout,
        handler_list: List[Handler],
        theme: str = "Dark Blue 3",
        window_timeout: int = None,
        window_kwargs: dict = dict(),
    ) -> None:
        self.handler = self.generate_handler(handler_list)
        if window_timeout is not None:
            assert window_timeout > 10, "timeoutは10ms以上を指定してください"
        #  オプションの設定と標準レイアウト
        sg.theme(theme)
        self.error_message = ""
        self.window = sg.Window(
            app_name, layout.get_layout(), **window_kwargs)
        self.window_timeout = window_timeout

    def generate_handler(self, handler_list: List[Handler]):
        ret_handler = handler_list[0](self)
        if len(handler_list) == 0:
            return handler
        for handler in handler_list[1:]:
            ret_handler = handler(self, successor=ret_handler)
        return ret_handler

    def run(self) -> None:
        while True:
            # self.window.enable()
            event, values = self.window.read(timeout=self.window_timeout)
            if event in (None, "Cancel"):
                break
            self.handler.handle(event, values)

    def popup_error(self, error_message=None):
        self.popup_error_hook()
        if error_message is not None:
            sg.popup_error(error_message)
        else:
            sg.popup_error(self.error_message)
        self.error_message = ""

    def popup_ok_cancel(self, message=None) -> bool:
        if message is None:
            message = self.error_message
            message += "\n\n処理を続行しますか？"
        ok = sg.popup_ok_cancel(message)
        self.error_message = ""
        return ok

    def popup_error_hook(self):
        pass

    def is_not_int(self, value, display_name):
        return not self.__try_convert_func(value, int, display_name)

    def is_not_float(self, value, display_name):
        return not self.__try_convert_func(value, float, display_name)

    def is_negative(self, value, display_name):
        if value < 0:
            self.error_message = "正の値を入力してください\n"
            self.error_message += f"入力値  {display_name}:{value}\n"
            return True
        return False

    def extension_is_not(self, extension, s):
        if osp.splitext(s)[1] != extension:
            self.error_message = f"拡張子が{extension}ではありません。\n"
            self.error_message += f"現在の拡張子: {osp.splitext(s)[1]}\n"
            return True
        return False

    def is_not_empty_folder(self, folder_path):
        if not self.__is_empty(folder_path):
            self.error_message = f"フォルダが空ではありません。\n{folder_path}\n"
            return True
        return False

    def is_empty_folder(self, folder_path):
        if self.__is_empty(folder_path):
            self.error_message = f"フォルダが空です。\n{folder_path}\n"
            return True
        return False

    def __is_empty(self, folder_path: str) -> bool:
        return len(glob.glob(osp.join(folder_path, "*"))) == 0

    def __try_convert_func(self, x, func, display_name, msg="有効な値を入力してください\n"):
        try:
            assert callable(func)
            func(x)
            return True
        except ValueError:
            self.error_message = msg
            self.error_message += f"入力値  {display_name}:{x}\n"
            return False

    def not_exists(self, path):
        if type(path) == str:
            if not osp.exists(path):
                self.error_message = "フォルダまたはファイルが存在しません\n"
                self.error_message += f"入力値: {path}\n"
                return False
        elif type(path) == list:
            judge_sum = sum([osp.exists(p) for p in path if p is not None])
            if judge_sum > 0:
                return False
        else:
            self.error_message = "フォルダまたはファイルの指定は、文字列またはそのリストで行ってください。"
            return False
        return True
