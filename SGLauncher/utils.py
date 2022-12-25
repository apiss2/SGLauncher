import sys
import os.path as osp

import numpy as np
import PySimpleGUI as sg

try:
    import cv2
except ImportError:
    pass


def try_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            exc_type, _, exc_tb = sys.exc_info()
            fname = osp.split(exc_tb.tb_frame.f_code.co_filename)[1]
            msg = f'exc_type: {exc_type}, fname: {fname}, line: {exc_tb.tb_lineno}'
            sg.popup_error(msg + f'\n{e}')
    return wrapper


class SquareResizePad:
    def __init__(
        self,
        target_size,
        pad_value=(0, 0, 0),
        grayscale=True
    ):
        """
        画像が指定サイズの正方形になるようにパディングする

        Args:
        target_size(int): 正方形の画像のターゲットサイズ。
        pad_value(tuple(int)): 回転した画像をパディングするためのカラー値。
        """
        assert isinstance(target_size, int)
        if grayscale:
            assert isinstance(pad_value, int)
        else:
            assert isinstance(pad_value, tuple)
            assert len(pad_value) == 3

        self.target_size = target_size
        self.pad_value = pad_value
        self.grayscale = grayscale

    def resize_img(self, img, keep_ratio=True):
        h, w = img.shape[:2]
        if keep_ratio:
            t_h = self.target_size if h >= w else int(h * self.target_size / w)
            t_w = self.target_size if h <= w else int(w * self.target_size / h)
        else:
            t_h = t_w = self.target_size
            img = cv2.resize(img, (t_w, t_h))
        return img

    def square_pad(self, img):
        h, w = img.shape[:2]
        if h == w:
            return img
        pad_size = max(h, w)
        shape = (pad_size, pad_size) if self.grayscale else (pad_size, pad_size, 3)
        expand_img = np.ones(shape, dtype=np.uint8)
        expand_img[:] = self.pad_value
        if h > w:
            y0, x0 = 0, (h - w) // 2
        else:
            y0, x0 = (w - h) // 2, 0
        expand_img[y0:y0 + h, x0:x0 + w] = img
        return expand_img

    def __call__(self, img) -> np.array:
        img = self.resize_img(img, keep_ratio=True)
        img = self.square_pad(img)
        return img

    def __repr__(self):
        return self.__class__.__name__
