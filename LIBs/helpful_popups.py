from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex as C
from plyer import notification, audio
from threading import Thread


def notify(title="Notification", message="notification message", timeout=5):
    notification.notify(title=title, message=message, timeout=timeout, app_icon="Images/icon.png",
                        app_name="NOTIFICATION", ticker="1")
    # use notification with
    audio.start()  # only for android


class Popup_utilities:
    def __init__(self):
        # input popup variables
        self.input_box_output = None
        # warning popup variables
        self.warning_popup_closed = None
        # waiting popup variables
        self.popup_wait = None
        self.wait_text = None
        self.open_wait_popup = None
        self.wait_schedule = None
        self.shrink_size = False

    # ========== waiting popup.
    def start_waiting_popup(self, title=" ", separator_color=(0, 0, 0, 0), text="Please Wait", *args):
        if not self.open_wait_popup:
            print("popup opened", title, text)
            self.waiting_popup(title, separator_color, text)
            self.wait_schedule = Clock.schedule_interval(self.wait_clock, 1)
            self.open_wait_popup = True

    def wait_clock(self, *args):
        widget = self.wait_text
        if widget.text == ". . . ":
            widget.text = ""
        else:
            widget.text += ". "

    def waiting_popup(self, title, separator_color, text):
        box = BoxLayout(orientation="vertical", spacing=10, padding=10)
        self.wait_text = Label(text=". ", color=(0, 0, 1), font_size="34sp")
        box.add_widget(Label(text="", size_hint_y=0.1))
        box.add_widget(Label(text=text, size_hint_y=0.1, font_size="30sp"))
        box.add_widget(self.wait_text)
        if self.shrink_size:
            size_hint = (0.4, 0.2)
        else:
            size_hint = (0.75, 0.3)
        self.popup_wait = Popup(title=title, content=box, size_hint=size_hint, auto_dismiss=False,
                                separator_color=separator_color, title_align="center")
        self.popup_wait.background_color = C("#041a4a99")
        self.popup_wait.open()

    def stop_waiting_popup(self, *args):
        if self.open_wait_popup:
            self.wait_schedule.cancel()
            self.popup_wait.dismiss()
            print("popup closed")
            self.open_wait_popup = False

    # =========

    def warning_popup(self, text, title="Warning", separator_color=C("#0000aa00")):
        self.warning_popup_closed = False

        def _close_popup(*args):
            if warning_popup:
                warning_popup.dismiss()
            self.warning_popup_closed = True

        box = BoxLayout(orientation="vertical", spacing=10, padding=10)
        button = Button(text="Continue", size_hint_y=0.3, font_size="20sp", color=C("#020fffff"),
                        background_color=C("#041a4a00"))
        box.add_widget(Label(text="", size_hint_y=0.1))
        box.add_widget(Label(text=text, size_hint_y=0.3, font_size="20sp", markup=True))
        box.add_widget(button)
        warning_popup = Popup(title=title, content=box, size_hint=(0.75, 0.35), separator_color=separator_color,
                              background_color=C("#041a4aff"), auto_dismiss=False)
        warning_popup.open()
        button.bind(on_release=_close_popup)

    def choose_popup(self, text, button_text_1, button_text_2, title="Choose An Option",
                     separator_color=C("#0000aa00"), execute_function=None):

        def _close_popup(*args):
            choose_popup.dismiss()
            if execute_function is not None:
                execute_function()

        def _set_output_1(*args):
            self.choose_box_output = True
            _close_popup()

        def _set_output_2(*args):
            self.choose_box_output = False
            _close_popup()

        box = BoxLayout(orientation="vertical", spacing=10, padding=10)
        chooseBox = BoxLayout(orientation="horizontal", spacing=10, padding=10)
        button1 = Button(text=button_text_1, font_size="20sp", color=C("#020fffff"),
                         background_color=C("#041a4a00"))
        button2 = Button(text=button_text_2, font_size="20sp", color=C("#020fffff"),
                         background_color=C("#041a4a00"))
        chooseBox.add_widget(button1)
        chooseBox.add_widget(button2)
        box.add_widget(Label(text="", size_hint_y=0.1))
        box.add_widget(Label(text=text, size_hint_y=0.3, font_size="20sp", markup=True))
        box.add_widget(chooseBox)
        choose_popup = Popup(title=title, content=box, size_hint=(0.75, 0.35), separator_color=separator_color,
                             background_color=C("#041a4aee"), auto_dismiss=True)
        choose_popup.open()
        button1.bind(on_release=_set_output_1)
        button2.bind(on_release=_set_output_2)

    def input_popup(self, text, button_text, title="Input", separator_color=C("#0000aa00"), execute_function=None):

        def _close_popup(*args):
            input_popup.dismiss()
            if execute_function is not None:
                execute_function()

        def _set_output(*args):
            self.input_box_output = input_box.text
            _close_popup()

        box = BoxLayout(orientation="vertical", spacing=20, padding=10)
        input_box = TextInput(text="", multiline=False, size_hint_y=0.35, font_size="20sp",
                              background_color=C("#049a4aff"), foreground_color=C("#020ffbff"),
                              cursor_color=(0, 0, 1, 1))
        button = Button(text=button_text, size_hint_y=0.25, font_size="20sp", color=C("#020fffff"),
                        background_color=C("#041a4a00"))
        box.add_widget(Label(text=text, size_hint_y=0.3, font_size="20sp", markup=True))
        box.add_widget(input_box)
        box.add_widget(button)
        input_popup = Popup(title=title, content=box, size_hint=(0.75, 0.35), separator_color=separator_color,
                            background_color=C("#041a4aee"), auto_dismiss=True)
        input_popup.open()
        button.bind(on_release=_set_output)
        input_box.bind(on_text_validate=_set_output)
