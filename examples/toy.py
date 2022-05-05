import PySimpleGUI as sg
from PyTooSimpleGUI import App, Handler, Layout


class MyLayout(Layout):
    def get_keys(self):
        return ['hello', 'sleep']

    def get_layout(self) -> list:
        layout = [
            [sg.Text('どちらかのボタンを押す')],
            [sg.Button('hello'), sg.Button('sleep')]
            ]
        return layout


class HelloWorldHandler(Handler):
    def __init__(self, app: App, successor=None):
        super().__init__(app, successor, event='hello')

    def proc(self, values):
        sg.popup('Hello, World!')


class GoodNightHandler(Handler):
    def __init__(self, app: App, successor=None):
        super().__init__(app, successor, event='sleep')

    def proc(self, values):
        sg.popup('Good Night!')


if __name__ == '__main__':
    handlers = [HelloWorldHandler, GoodNightHandler]
    layout = MyLayout()
    app = App('Toy App', layout, handler_list=handlers)
    app.run()

