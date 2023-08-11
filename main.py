#! /usr/bin/env python3
from threading import Thread
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy import Config
from kivy.core.text import LabelBase
from plyer import notification, audio
from kivy.lang import Builder
from LIBs.helpful_popups import Popup_utilities, notify
from LIBs.server_connector import ServerConnector
from LIBs.topo_designer import TopoDesigner, C
from LIBs.audio import Audio
from LIBs.text_box import EditedTextInput

Builder.load_file("LIBs/KVFiles/Templates.kv")

window_size = (900, 600)


class Main_widget(ScreenManager):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        # to access SDN_EXPLORERApp class
        self.link_widgets = None
        self.switch_widgets = None
        self.app = app
        self.notify = notify
        self.server_connector = ServerConnector()
        self.helpful_popups = Popup_utilities()
        self.helpful_popups.shrink_size = True
        self.topo_designer = TopoDesigner(self.ids.play_area.width, self.ids.play_area.height)

    def check_server_connection(self, ip_address, port):
        """
        check if the ip address and port are valid,
        then connect to the server and move to the main screen.
        :param ip_address:
        :param port:
        :return:
        """
        if self.server_connector.connect(ip_address, port):
            self.server_connector.receive_loop(func=self.change_in_data_detected)
            self.current = "main_screen"
            Window.maximize()
            max_width, max_height = Window.size
            self.ids.play_area.size = (max_width, max_height)
            self.load_data()
        else:
            self.helpful_popups.warning_popup("Connection to the server failed.")

    def load_data(self, max_wait_time=5):
        """
        load data from the server for a while, then stop.
        :param max_wait_time: maximum time to wait for data.
        :return: it calls process_data() function.
        """

        def pass_data_to_designer(dt):
            if not self.server_connector.received_data:
                return
            data = self.server_connector.received_data["Data"]
            self.topo_designer.handle_received_data(data)
            if self.topo_designer.no_change_counter > max_wait_time:
                self.topo_designer.no_change_counter = 0
                call_func.cancel()
                self.topo_designer.fetch_data()
                self.helpful_popups.stop_waiting_popup()
                Clock.schedule_once(self.process_data, 1)

        def pass_data_to_designer_callback():
            self.helpful_popups.start_waiting_popup(title="", text="Loading data")
            callFunc = Clock.schedule_interval(pass_data_to_designer, 1)
            return callFunc

        call_func = pass_data_to_designer_callback()

    def change_in_data_detected(self):
        print("change in data detected")

    def process_data(self, *args):
        """
        process data from the server.
        :return:
        """

        def first_stage_thread(*args):
            self.topo_designer.first_process()
            # self.helpful_popups.stop_waiting_popup()
            self.helpful_popups.start_waiting_popup(title="", text="Drawing topology")
            Clock.schedule_once(second_stage_thread, 0.1)

        def second_stage_thread(*args):
            self.topo_designer.second_process(self.topo_designer.min_combo[1])
            self.add_topo()
            self.helpful_popups.stop_waiting_popup()

        # self.helpful_popups.start_waiting_popup(title="Please Wait", text="Processing data")
        Clock.schedule_once(first_stage_thread, 0.1)
        # self.topo_designer.first_process()
        # self.helpful_popups.stop_waiting_popup()
        # self.helpful_popups.start_waiting_popup(title="Please Wait", text="Drawing topology")
        # self.topo_designer.second_process(self.topo_designer.min_combo[1])
        # self.add_topo()
        # self.helpful_popups.stop_waiting_popup()

    def add_topo(self):
        """
        add the topology to the play area.
        :return:
        """
        self.switch_widgets, self.link_widgets = self.topo_designer.draw_topo()

        for switch_widget in self.switch_widgets:
            self.ids.play_area.add_widget(switch_widget)

        for link_widget in self.link_widgets:
            self.ids.play_area.add_widget(link_widget)

    def reprocess_data(self, *args):
        self.ids.play_area.clear_widgets()  # clear the widgets
        self.ids.play_area.canvas.clear()  # clear the canvas
        self.topo_designer.dpids_dict = {}
        self.topo_designer.fetch_data()
        self.process_data()
        self.add_topo()

    def on_touch_down(self, touch):
        """
        to detect the touch on the play area.
        :param touch:
        :return:
        """
        if ScreenManager.on_touch_down(self, touch):
            return True
        if self.ids.play_area.collide_point(*touch.pos):
            Window.set_system_cursor("Images/tap.png")
            # check if the touch is on a switch
            for switch in self.switch_widgets:
                switch.size = self.topo_designer.switch_size
                if switch.collide_point(*touch.pos):
                    print("switch touched", touch.pos, switch.pos, switch.size, switch.dpid)
                    if switch.pos in self.topo_designer.location_to_widget_dict.keys():
                        print("from topo designer:", self.topo_designer.location_to_widget_dict[switch.pos])


class SDN_EXPLORERApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        widget = Main_widget(self)
        return widget

    def on_start(self):
        # self.root_window.size = window_size
        self.root_window.resizable = False

    def on_stop(self):
        self.root.server_connector.stop_receive_thread = True
        self.root.server_connector.socket.close()


if __name__ == "__main__":
    # adding fonts, you can call them using font_name property.
    LabelBase.register('fonts', 'Fonts/ArialUnicodeMS.ttf')
    LabelBase.register("shapes", "Fonts/modernpics.otf")

    # to adjust the app when the keyboard rises
    from kivy.core.window import Window

    Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
    Window.softinput_mode = "below_target"
    # to add a color in the background of the app.
    Window.clearcolor = (169.0 / 255, 172.0 / 255, 175.0 / 255, 0)
    Window.size = window_size

    SDN_EXPLORERApp().run()
