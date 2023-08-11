from kivy.utils import get_color_from_hex as C
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


class EditedTextInput(TextInput):
    pass


class ChatBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "10sp"
        self.padding = "10sp"
        self.size_hint_y = None
        self.height = 40
        self.background_color = C("#aaaaaaaa")
        self.messages = []

    def message_received(self, message):
        self.messages.append(message)
        label = Label(text=message, height="40sp", halign="left",
                      font_name="arabic_font", font_size="20sp", text_size=(self.width, None),
                      color=C("#aaaaffff"), opacity=0.8)
        self.add_widget(label)
        self.height += label.height * 1.6 + 15

    def send_message(self, message):
        self.messages.append(message)
        label = Label(text=message, height="40sp", halign="right",
                      font_name="arabic_font", font_size="20sp", text_size=(self.width, None),
                      color=C("#aaffaaff"), opacity=0.8)
        self.add_widget(label)
        self.height += label.height * 1.6 + 15


class ChatPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.delete_button = None
        self.input_box = None
        self.scroll_view = None
        self.chat_box = None
        self.title = "Chat Room"
        self.size_hint = [0.8, 0.8]
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.auto_dismiss = True
        self.active = False
        self.init_build()

    def init_build(self):
        self.delete_button = Button(text="\u0049", size_hint_x=0.1, background_color=C("#77777700"), font_name="shapes"
                                    , font_size="30sp")
        self.input_box = EditedTextInput(underscore_line=True, shrank=True, background_color=C("#777777")
                                         , font_size="20sp", font_name="arabic_font", hint_text="Enter Your Message",
                                         hint_text_color=C("#00000055"), padding=[10, 10, 10, 10],
                                         foreground_color=C("#000000ff"), borders_color=C("#00000055"))
        self.chat_box = ChatBox()
        self.scroll_view = ScrollView(size_hint_y=0.87)
        self.scroll_view.add_widget(self.chat_box)
        structBox = BoxLayout(orientation="vertical", spacing="10sp", padding="10sp")
        structBox.add_widget(self.scroll_view)
        input_box = BoxLayout(orientation="horizontal", spacing="10sp", padding="10sp", size_hint_y=0.12)
        input_box.add_widget(self.delete_button)
        input_box.add_widget(self.input_box)
        structBox.add_widget(input_box)
        self.add_widget(structBox)
        self.input_box.bind(on_text_validate=self.send_message)
        self.delete_button.bind(on_press=self.clear_chatBox)

    def clear_chatBox(self, instance):
        self.chat_box.clear_widgets()
        self.chat_box.messages = []

    def send_message(self, instance):
        if self.input_box.text != "":
            self.chat_box.send_message(self.input_box.text)
            self.input_box.text = ""
            # self.scroll_view.scroll_y = 0

    def load_data(self, data):
        self.chat_box.clear_widgets()
        self.chat_box.messages = []
        for message in data.split("\n"):
            if message != "":
                self.chat_box.message_received(message)

    def on_open(self):
        self.active = True
        super().on_open()

    def on_dismiss(self):
        self.active = False
        super().on_dismiss()
