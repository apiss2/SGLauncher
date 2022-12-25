import PySimpleGUI as sg
from SGLauncher import App, Layout, EventHandler


class MyLayout(Layout):
    def get_keys(self):
        return ['hello', 'sleep']

    def get_layout(self) -> list:
        layout = [
            [sg.Text('どちらかのボタンを押す')],
            [sg.Button('hello'), sg.Button('sleep')]
            ]
        return layout


class HelloWorldHandler(EventHandler):
    def __init__(self, app: App, successor=None):
        super().__init__(app, successor, trigger='hello')

    def proc(self, values):
        sg.popup('Hello, World!')


class GoodNightHandler(EventHandler):
    def __init__(self, app: App, successor=None):
        super().__init__(app, successor, trigger='sleep')

    def proc(self, values):
        sg.popup('Good Night!')


if __name__ == '__main__':
    handlers = [HelloWorldHandler, GoodNightHandler]
    layout = MyLayout()
    app = App('Toy App', layout, handler_list=handlers, resizable=True)
    app.run()

