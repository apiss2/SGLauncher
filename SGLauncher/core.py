from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import List, Optional

import PySimpleGUI as sg

from .__base__ import AppBase

try:
    import cv2
except ImportError:
    pass


class Layout(metaclass=ABCMeta):
    @abstractmethod
    def get_layout(self) -> list:
        pass


class Handler(metaclass=ABCMeta):
    def __init__(
        self,
        app: App,
        successor: Optional[Handler] = None,
        trigger: Optional[str] = None,
        break_after_proc: bool = True
    ):
        self.__successor = successor
        self.app: App = app
        self.trigger: Optional[str] = trigger
        self.break_after_proc = break_after_proc

    @abstractmethod
    def proc(self, values):
        '''
        条件に該当した場合走らせる処理。
        処理終了後は他の処理を行わずにループの最初に戻る.
        '''
        pass

    @abstractmethod
    def is_triggered(self, event, values) -> bool:
        pass

    def default_proc(self, values):
        '''
        デフォルトで走らせる処理。
        処理終了後は他の処理に移行する。
        '''
        pass

    def handle(self, event, values):
        if self.is_triggered(event, values):
            self.proc(values)
            if self.break_after_proc:
                return
            else:
                self.default_proc(values)
        if self.__successor is not None:
            self.__successor.handle(event, values)


class App(AppBase):
    def __init__(
        self,
        app_name: str,
        layout: Layout,
        handler_list: List[Handler],
        theme: str = "Default 1",
        window_timeout: int = None,
        **window_kwargs
    ) -> None:
        super().__init__(theme)
        self.handler: Handler = self.__generate_handler(handler_list[::-1])
        if window_timeout is not None:
            assert window_timeout > 10, "timeoutは10ms以上を指定してください"
        # オプションの設定と標準レイアウト
        self.window = sg.Window(app_name, layout.get_layout(), **window_kwargs)
        self.window_timeout = window_timeout

    def __generate_handler(self, handler_list: List[Handler]):
        '''
        複数のハンドラを受け取って一つにまとめるメソッド
        '''
        ret_handler = handler_list[0](self)
        if len(handler_list) == 0:
            return ret_handler
        for handler in handler_list[1:]:
            ret_handler = handler(self, successor=ret_handler)
        return ret_handler

    def run(self) -> None:
        while True:
            event, values = self.window.read(timeout=self.window_timeout)
            if event in (None, "Cancel"):
                break
            self.handler.handle(event, values)

    def update_window(self, image, window_name) -> bool:
        '''
        指定されたウィンドウの画像を更新するメソッド
        '''
        if window_name not in self.window.key_dict.keys():
            self.popup_error(f'指定されたウィンドウが存在しません: {window_name}')
            return False
        if image is None:
            self.window[window_name].update(data=None)
            return False
        imgbytes = cv2.imencode(".png", image)[1].tobytes()
        self.window[window_name].update(data=imgbytes)
        return True


class EventHandler(Handler):
    """
    イベント（ボタン類など）が発生した際の処理を行うクラス
    """
    @abstractmethod
    def proc(self, values):
        pass

    def is_triggered(self, event, values):
        return event == self.trigger


class ValueHandler(Handler):
    """
    GUIの状態（チェックボックスなど）に応じた処理を記述するクラス
    """
    @abstractmethod
    def proc(self, values):
        pass

    def is_triggered(self, event, values):
        return values[self.trigger]


class StateHandler(Handler):
    """
    App内のブール値にしたがって処理を行うクラス
    """
    @abstractmethod
    def proc(self, values):
        pass

    def is_triggered(self, event, values):
        if not self.app.have(self.trigger):
            return False
        value = self.app[self.trigger]
        if not isinstance(value, bool):
            return False
        return value
