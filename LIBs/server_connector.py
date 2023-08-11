import socket
from threading import Thread
import pickle


class ServerConnector:
    def __init__(self, buffer_size=1024):
        self.change_in_data_detected = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer_size = buffer_size
        self.data_pdu = {"Header": "MT", "MessageType": "Inform", "DataType": "Links", "Data": {}}
        self.stop_receive_thread = False
        self.receive_thread = None
        self.host = None
        self.port = None
        self.received_data = None
        self.previous_data = self.data_pdu.copy()

    def connect(self, host, port):
        try:
            self.host = host
            self.port = port
            self.socket.connect((host, port))
            return True
        except Exception as e:
            print(e)
            return False

    def receive(self):
        try:
            received_data = self.socket.recv(self.buffer_size)
            return pickle.loads(received_data)
        except Exception as e:
            print(e, "in receive function")
            return None

    def receive_loop(self, func=None):
        if func:
            self.change_in_data_detected = func
        self.receive_thread = Thread(target=self._receive_thread)
        self.receive_thread.start()

    def _receive_thread(self):
        while not self.stop_receive_thread:
            self.received_data = self.receive()
            if self.received_data:
                self.detect_change_in_data()
            # print(self.received_data)

    def detect_change_in_data(self):
        if self.received_data["MessageType"] == "Inform" and self.received_data["DataType"] == "Links":
            if self.received_data["Data"] != self.previous_data["Data"]:
                if not self.previous_data["Data"]:
                    self.previous_data = self.received_data
                    return
                print("From server_connector.py: change in data detected")
                self.change_in_data_detected()
                self.previous_data = self.received_data
