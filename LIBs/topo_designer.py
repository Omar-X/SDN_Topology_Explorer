from kivy.graphics import Color, Line, RoundedRectangle
from kivy.properties import NumericProperty, StringProperty, ListProperty, BooleanProperty
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.utils import get_color_from_hex as C
from LIBs.helpful_popups import Popup_utilities
import math


class RotatedTextLabel(FloatLayout):
    angle = NumericProperty(0)
    text = StringProperty("")
    font_size = StringProperty("10sp")
    color = ListProperty(C("#000000"))
    at_start = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(RotatedTextLabel, self).__init__(**kwargs)
        self.text_instructions = None
        self.text = kwargs["text"]
        self.angle = kwargs["angle"]
        self.font_size = kwargs["font_size"]
        self.color = kwargs["color"]


def get_combination(switches_list, number):
    """
    :param switches_list: list of switches
    :param number: combo number
    :return: the combination corresponding to the number
    """

    def swap(array, i, j):
        array[i], array[j] = array[j], array[i]

    # calculate reminder and quotient
    reminder = number % len(switches_list)
    quotient = number // len(switches_list)

    if quotient:
        if quotient < len(switches_list):
            swap(switches_list, quotient - 1, quotient)
        else:
            pass

    if reminder:
        swap(switches_list, 0, reminder - 1)

    return switches_list


def two_locations_distance(loc_1, loc_2):
    return math.sqrt((loc_1[0] - loc_2[0]) ** 2 + (loc_1[1] - loc_2[1]) ** 2)


class TopoDesigner:
    def __init__(self, max_width=1000, max_height=1000):
        # process properties
        self.min_combo = None
        self.map_locations = None
        self.location_to_widget_dict = {}  # {location: widget}
        # weired line properties
        self.line_width = 2
        self.line_min_length = 150
        self.normal_line_color = C("#000000aa")
        self.no_flood_line_color = C("#ff0000aa")
        self.inactive_line_color = C("#00000060")
        # switch properties
        self.switch_size = (50, 50)
        self.switch_radius = 10
        self.switches_min_distance = 20
        self.active_switch_color = C("#000000ff")
        self.inactive_switch_color = C("#00000077")
        # map properties | need to check the map size later
        self.max_width = max_width
        self.max_height = max_height
        # received packets properties
        self.no_change_counter = 0
        self.dpids_dict = {}
        self.switches_dpids = set()
        self.switches_links = set()
        self.no_flood_links = set()

    def weired_line(self, start_pos, end_pos, start_text="", end_text="", allow_flood=True, active=True):
        """
        :param active:  if True, means the link is can be used
        :param allow_flood: if True, means the link allow flood packets
        :param end_text:  text to be written at the end of the line
        :param start_text:  text to be written at the start of the line
        :param start_pos: tuple of (x, y) coordinates
        :param end_pos: tuple of (x, y) coordinates
        :return: a line widget
        """
        if start_pos[1] > end_pos[1]:
            start_pos, end_pos = end_pos, start_pos
            start_text, end_text = end_text, start_text

        x1, y1 = start_pos
        x2, y2 = end_pos
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        x1 += self.switch_size[0] * math.cos(math.radians(angle)) / 2
        x2 -= self.switch_size[0] * math.cos(math.radians(angle)) / 2
        y1 += self.switch_size[1] * math.sin(math.radians(angle)) / 2
        y2 -= self.switch_size[1] * math.sin(math.radians(angle)) / 2

        print("angle: ", angle, "sin: ", math.sin(math.radians(angle)), "cos: ", math.cos(math.radians(angle)))
        print(x1, y1, x2, y2)

        line_widget = Widget()
        init = 8 + 20 * abs(angle) / 90 if -90 <= angle <= 90 else 8 + 20 * (180 - abs(angle)) / 90
        if start_text != "":
            if -90 <= angle <= 90:
                text_pos_1 = (x1 - init * math.sin(math.radians(angle)) + 15 * math.cos(math.radians(angle)),
                              y1 + init * math.cos(math.radians(angle)) + 15 * math.sin(math.radians(angle)))
            else:
                print("angle: ", angle, "sin: ", math.sin(math.radians(angle)), "cos: ", math.cos(math.radians(angle)))
                text_pos_1 = (x1 + init * math.cos(math.radians(angle - 90)) + 35 * math.cos(math.radians(angle)),
                              y1 + init * math.sin(math.radians(angle - 90)) + 10 * math.sin(math.radians(angle)))
            start_label = RotatedTextLabel(text=start_text, angle=angle, pos=text_pos_1, at_start=True,
                                           size=(self.switch_size[0], 15), font_size="15sp", color=C("#000000"))
            line_widget.add_widget(start_label)

        if end_text != "":
            if -90 <= angle <= 90:
                text_pos_2 = (x2 - init * math.sin(math.radians(angle)) - 50 * math.cos(math.radians(angle)),
                              y2 + init * math.cos(math.radians(angle)) - 50 * math.sin(math.radians(angle)))
            else:
                text_pos_2 = (x2 + init * math.cos(math.radians(angle - 90)) - 35 * math.cos(math.radians(angle)),
                              y2 + init * math.sin(math.radians(angle - 90)) - 55 * math.sin(math.radians(angle)))
            end_label = RotatedTextLabel(text=end_text, angle=angle, pos=text_pos_2, at_start=False,
                                         size=(self.switch_size[0], 15), font_size="15sp", color=C("#000000"))
            line_widget.add_widget(end_label)

        with line_widget.canvas:
            Color(rgba=(self.normal_line_color if allow_flood else self.no_flood_line_color) if active
            else self.inactive_line_color)
            Line(points=(x1, y1, x2, y2), width=self.line_width)

        return line_widget

    def switch(self, dpid_number, location, active=True):
        """
        :param active: if True, means the switch is active
        :param dpid_number: switch datapath id
        :param location: tuple of (x, y) coordinates
        :return: a switch widget
        """
        x, y = location
        x -= self.switch_size[0] / 2
        y -= self.switch_size[1] / 2
        switch_widget = Widget()
        switch_widget.pos = (x, y)
        switch_widget.size = (self.switch_size[0], self.switch_size[1])
        print("switch size: ", self.switch_size)
        switch_widget.dpid = "dpid: " + str(dpid_number)
        with switch_widget.canvas.before:
            Color(rgba=self.active_switch_color if active else self.inactive_switch_color)
            round_rectangle = RoundedRectangle(pos=(x, y), size=self.switch_size, radius=[self.switch_radius])
            round_rectangle.source = "Images/hub.png"

        label = Label(text="dpid: " + str(dpid_number), pos=(x, y - 10), size=(self.switch_size[0], 15),
                      font_size="20sp", color=C("#000000ff"))
        switch_widget.add_widget(label)
        return switch_widget

    def set_equal_points(self, number_of_points):
        """
        :param number_of_points: number of points to be distributed equally
        :return: list of points
        """
        points = []
        columns = math.ceil(math.sqrt(number_of_points))
        rows = math.ceil(number_of_points / columns)
        row = 1
        unit_width = self.max_width / (columns + 1)
        unit_height = self.max_height / (rows + 1)
        self.line_min_length = min(unit_width, unit_height) / 1.3

        for i in range(number_of_points):
            if i % columns == 0:
                row += 1
            points.append((unit_width * (i % columns + 1), unit_height * row))

        return points

    def handle_received_data(self, data):
        if not data:
            self.no_change_counter = 0
            return
        if self.switches_dpids == data["SWITCHES_DPIDS"] and self.switches_links == data["SWITCHES_LINKS"] and \
                self.no_flood_links == data["NO_FLOOD_LINKS"]:
            self.no_change_counter += 1
        else:
            self.no_change_counter = 0
        self.switches_dpids = data["SWITCHES_DPIDS"]
        self.switches_links = data["SWITCHES_LINKS"]
        self.no_flood_links = data["NO_FLOOD_LINKS"]

    def fetch_data(self):
        for link in self.switches_links:
            link_list = link.split("-")
            switch_1 = "dpid:" + link_list[0]
            if switch_1 in self.dpids_dict.keys():
                self.dpids_dict[switch_1]["links"].append((int(link_list[1]), int(link_list[2])))
            else:
                self.dpids_dict[switch_1] = {"location": None, "links": []}
                self.dpids_dict[switch_1]["location"] = (0, 0)
                self.dpids_dict[switch_1]["links"].append((int(link_list[1]), int(link_list[2])))

            switch_2 = "dpid:" + link_list[2]
            if switch_2 in self.dpids_dict.keys():
                self.dpids_dict[switch_2]["links"].append((int(link_list[3]), int(link_list[0])))
            else:
                self.dpids_dict[switch_2] = {"location": None, "links": []}
                self.dpids_dict[switch_2]["location"] = (0, 0)
                self.dpids_dict[switch_2]["links"].append((int(link_list[3]), int(link_list[0])))

    def set_random_locations(self, number):
        """
        Set random locations for switches using the get_combination function
        :param number:
        :return:
        """
        combo = get_combination(list(self.dpids_dict.keys()), number)
        for index, dpid in enumerate(combo):
            self.dpids_dict[dpid]["location"] = list(self.map_locations[index])

    def closest_switch_len(self, switch_id):
        """
        :param switch_id:
        :return: the length of the closest switch to the given location
        """
        min_len = 100000
        for switch in self.dpids_dict.keys():
            if switch != switch_id:
                length = two_locations_distance(self.dpids_dict[switch]["location"], self.dpids_dict[switch_id]["location"])
                if length < min_len:
                    min_len = length
        return min_len

    def total_links_length(self):
        """
        Calculate the total length of links, and check if the length of any link is less than the minimum allowed length
        :return: total length of links, and a boolean value that indicates if the length of any link is less than the
        minimum allowed length
        """
        total = 0
        allowed = True
        for link_id in self.switches_links:
            dpid_1, dpid_2 = "dpid:" + link_id.split("-")[0], "dpid:" + link_id.split("-")[2]
            to_dpid_1_len = self.closest_switch_len(dpid_1)
            to_dpid_2_len = self.closest_switch_len(dpid_2)
            loc_1, loc_2 = self.dpids_dict[dpid_1]["location"], self.dpids_dict[dpid_2]["location"]

            distance = two_locations_distance(loc_1, loc_2)
            if distance < self.line_min_length:
                allowed = False
            if loc_1[0] < 0 or loc_1[1] < 0 or loc_2[0] < 0 or loc_2[1] < 0:
                allowed = False
            if loc_1[0] > self.max_width or loc_1[1] > self.max_height or loc_2[0] > self.max_width or \
                    loc_2[1] > self.max_height:
                allowed = False
            if to_dpid_1_len < self.line_min_length / 2 or to_dpid_2_len < self.line_min_length / 2:
                allowed = False

            total += two_locations_distance(loc_1, loc_2)
        return total, allowed

    def first_process(self):
        """
        This function aims to distribute the switches in the best way possible to reduce the total length of links
        :return:
        """
        self.fetch_data()
        self.map_locations = self.set_equal_points(len(self.switches_dpids))

        # distribute the switches randomly
        max_iteration = len(self.switches_dpids) * (len(self.switches_dpids) - 1)
        max_iteration = 1000 if max_iteration > 1000 else max_iteration

        # get best combination
        self.set_random_locations(0)
        length, _ = self.total_links_length()
        min_combo = (0, length)  # a tuple of mix number and length
        for mix in range(1, max_iteration):
            self.set_random_locations(mix)
            length, _ = self.total_links_length()
            if length < min_combo[1]:
                min_combo = (mix, length)

        # set the best combination
        self.set_random_locations(min_combo[0])
        print("min_combo", min_combo)
        self.min_combo = min_combo
        return min_combo

    def second_process(self, topo_links_length=None, max_iteration=8000, step=0.1):
        """
        This function aims to shift the switches to reduce the total length of links
        :param topo_links_length:  the total length of links in the topology to be reduced
        :param max_iteration:  maximum number of iterations
        :param step:  the step of shifting
        :return:
        """
        if topo_links_length is None:
            topo_links_length, _ = self.min_combo[1]
        min_len = topo_links_length
        step_size = step * self.line_min_length
        for iteration in range(max_iteration):
            for dpid in self.dpids_dict.keys():

                for x_direction in range(2):
                    self.dpids_dict[dpid]["location"][0] += step_size if not x_direction else -step_size
                    length, is_allowed = self.total_links_length()
                    if length < min_len and is_allowed:
                        min_len = length
                        break
                    else:
                        self.dpids_dict[dpid]["location"][0] -= step_size if not x_direction else -step_size

                for y_direction in range(2):
                    self.dpids_dict[dpid]["location"][1] += step_size if not y_direction else -step_size
                    length, is_allowed = self.total_links_length()
                    if length < min_len and is_allowed:
                        min_len = length
                        break
                    else:
                        self.dpids_dict[dpid]["location"][1] -= step_size if not y_direction else -step_size
        print("min_len", min_len)
        return min_len

    def draw_topo(self):
        """
        This function draws the topology on the screen using switch() and weired_line() functions, and read
        the data from self.dpids_dict
        :return: a list of switches and links widgets
        """
        switch_widgets = []
        link_widgets = []

        # draw switches
        for dpid in self.dpids_dict.keys():
            dpid_number = dpid.split(":")[1]
            switch_widget = self.switch(dpid_number, self.dpids_dict[dpid]["location"])
            switch_widgets.append(switch_widget)
            self.location_to_widget_dict[tuple(self.dpids_dict[dpid]["location"])] = {"switch": switch_widget}
            print("draw dpid", dpid, "location", self.dpids_dict[dpid]["location"])

        # draw links
        for link_id in self.switches_links:
            flood_allowed = False if link_id in self.no_flood_links else True
            dpid_1, dpid_2 = "dpid:" + link_id.split("-")[0], "dpid:" + link_id.split("-")[2]
            port_1, port_2 = "eth" + link_id.split("-")[1], "eth" + link_id.split("-")[3]
            loc_1, loc_2 = self.dpids_dict[dpid_1]["location"], self.dpids_dict[dpid_2]["location"]
            link_widget = self.weired_line(loc_1, loc_2, start_text=port_1, end_text=port_2, allow_flood=flood_allowed)
            link_widgets.append(link_widget)

            loc_1, loc_2 = tuple(loc_1), tuple(loc_2)

            if loc_1 not in self.location_to_widget_dict.keys():
                self.location_to_widget_dict[loc_1]["link"] = []
            elif "link" not in self.location_to_widget_dict[loc_1].keys():
                self.location_to_widget_dict[loc_1]["link"] = []

            if loc_2 not in self.location_to_widget_dict.keys():
                self.location_to_widget_dict[loc_2]["link"] = []
            elif "link" not in self.location_to_widget_dict[loc_2].keys():
                self.location_to_widget_dict[loc_2]["link"] = []

            self.location_to_widget_dict[loc_1]["link"].append(link_widget)
            self.location_to_widget_dict[loc_2]["link"].append(link_widget)

        return switch_widgets, link_widgets
