# -*- coding: utf-8 -*-
import socket
import sys

from knxnet import *
from knxnet import knxnet


class connectionKNX:
    def __init__(self, gateway_ip, gateway_port):
        # -> in this example, for sake of simplicity, the two ports are the same.
        self.action = None
        self.gateway_ip = gateway_ip
        self.gateway_port = gateway_port
        self.data_endpoint = ('0.0.0.0', 0)
        self.control_endpoint = ('0.0.0.0', 0)

        # -> Socket creation
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 3672))

        self.channel_id = None
        self.sequence_counter = None

    def send_data(self, data, data_size, acpi, dest_group_addr):
        """
        Send command data to a KNX enabled device
        :param data:
        :param data_size:
        :param acpi:
        :param dest_group_addr:
        :return:
        """

        #   -----------------------------------
        #   -> (0) Establish connection
        #   -----------------------------------

        self.establish_connection(data, acpi, data_size, dest_group_addr)

        #   -----------------------------------
        #   -> (1) Send tunneling ack request
        #   -----------------------------------

        self.tunneling_ack_request()

        print('-----------------------------------')

        #   -----------------------------------
        #   -> (2) Disconnect request
        #   -----------------------------------

        disconnect_resp_object = self.disconnect_request()

        # <- Retrieving data from disconnect request
        disconnect_channel_id = disconnect_resp_object.channel_id
        disconnect_status = disconnect_resp_object.status
        print('Channel ID: ', disconnect_channel_id)
        print('Channel status: ', disconnect_status)

        print('-----------------------------------')

    def read_data(self, data, data_size, acpi, dest_group_addr):
        """
        Read data from a KNX enabled device
        :param data:
        :param data_size:
        :param acpi:
        :param dest_group_addr:
        :return:
        """
        #   -----------------------------------
        #   -> (0) Establish connection
        #   -----------------------------------

        self.establish_connection(data, data_size, acpi, dest_group_addr)

        #   -----------------------------------
        #   -> (1) Send tunneling ack request
        #   -----------------------------------

        # <- Send Tunneling ack
        tunnel_ack = knxnet.create_frame(knxnet.ServiceTypeDescriptor.TUNNELLING_ACK,
                                         self.channel_id,
                                         0,
                                         self.sequence_counter)

        self.sock.sendto(tunnel_ack.frame, (self.gateway_ip, self.gateway_port))

        # <- Read Status
        data_recv, addr = self.sock.recvfrom(1024)
        tunnel_resp_object = knxnet.decode_frame(data_recv)

        #   -----------------------------------
        #   -> (2) Disconnect request
        #   -----------------------------------

        disconnect_resp_object = self.disconnect_request()

        # <- Retrieving data from disconnect request
        disconnect_channel_id = disconnect_resp_object.channel_id
        disconnect_status = disconnect_resp_object.status
        print('Channel ID: ', disconnect_channel_id)
        print('Channel status: ', disconnect_status)

        print('-----------------------------------')

        return tunnel_resp_object.data

    def establish_connection(self, data, data_size, acpi, dest_group_addr):
        """
        Basic dialog between a client and the gateway to establish connection
        and exchange according data
        :param data: data to be sent: [0, 1] or [0..255]
        :param data_size: data size, in bytes: [1, 2]
        :param acpi: o for reading, 2 for writing
        :param dest_group_addr: x/y/z
        :return:
        """
        #   -----------------------------------
        #   -> (1) Sending Connection request
        #   -----------------------------------
        conn_resp_object = self.connection_request()
        # <- Retrieving channel_id & status from Connection response
        conn_channel_id = conn_resp_object.channel_id
        conn_status = conn_resp_object.status
        self.channel_id = conn_channel_id
        print('Channel ID: ', conn_channel_id)
        print('Channel status: ', conn_status)
        print('-----------------------------------')
        #   -----------------------------------
        #   -> (2) Sending Connection State request
        #   -----------------------------------
        state_resp_object = self.connection_state_request()
        # <- Retrieving channel_id & status from Connection State response
        state_channel_id = state_resp_object.channel_id
        state_status = state_resp_object.status
        print('Channel ID: ', state_channel_id)
        print('Channel status: ', state_status)
        print('-----------------------------------')
        #   -----------------------------------
        #   -> (3) Tunneling request
        #   -----------------------------------
        tunnel_resp_object = self.tunneling_request(data, data_size, dest_group_addr, acpi)
        # <- Retrieving data from Tunneling response
        tunnel_channel_id = tunnel_resp_object.channel_id
        tunnel_status = tunnel_resp_object.status
        self.sequence_counter = tunnel_resp_object.sequence_counter
        print('Channel ID: ', tunnel_channel_id)
        print('Channel status: ', tunnel_status)
        print('Sequence counter: ', self.sequence_counter)
        print('-----------------------------------')
        #   -----------------------------------
        #   -> (4) Tunneling request read
        #   -----------------------------------
        self.tunneling_request_read()

    def disconnect_request(self):
        print('#5 Disconnect request')
        disconnect_req = \
            knxnet.create_frame(knxnet.ServiceTypeDescriptor.DISCONNECT_REQUEST, self.channel_id, self.control_endpoint)
        conn_req_dtgrm = disconnect_req.frame  # -> Serializing
        self.sock.sendto(conn_req_dtgrm, (self.gateway_ip, self.gateway_port))

        # <- Receiving Tunneling response
        data_recv, addr = self.sock.recvfrom(1024)
        disconnect_resp_object = knxnet.decode_frame(data_recv)

        return disconnect_resp_object

    def tunneling_ack_request(self):
        print('#4 Tunneling ack request')
        tunneling_ack = \
            knxnet.create_frame(knxnet.ServiceTypeDescriptor.TUNNELLING_ACK,
                                self.channel_id,
                                self.sequence_counter)
        conn_req_dtgrm = tunneling_ack.frame  # -> Serializing
        self.sock.sendto(conn_req_dtgrm, (self.gateway_ip, self.gateway_port))

    def tunneling_request_read(self):
        print('#4 Tunneling request read')

        # <- Receiving Tunneling request response
        data_recv, addr = self.sock.recvfrom(1024)
        tunnel_requ_resp_object = knxnet.decode_frame(data_recv)

        return tunnel_requ_resp_object

    def tunneling_request(self, data, data_size, dest_group_addr, apci):
        print('#3 Tunneling request')
        tunneling_req = \
            knxnet.create_frame(knxnet.ServiceTypeDescriptor.TUNNELLING_REQUEST,
                                dest_group_addr,
                                self.channel_id,
                                data,
                                data_size,
                                apci)
        conn_req_dtgrm = tunneling_req.frame  # -> Serializing
        self.sock.sendto(conn_req_dtgrm, (self.gateway_ip, self.gateway_port))

        # <- Receiving Connection State response
        data_recv, addr = self.sock.recvfrom(1024)
        tunnel_resp_object = knxnet.decode_frame(data_recv)
        return tunnel_resp_object

    def connection_state_request(self):
        print('#2 Connection State request')
        conn_state_req = \
            knxnet.create_frame(knxnet.ServiceTypeDescriptor.CONNECTION_STATE_REQUEST,
                                self.channel_id, self.control_endpoint)
        conn_req_dtgrm = conn_state_req.frame  # -> Serializing
        self.sock.sendto(conn_req_dtgrm, (self.gateway_ip, self.gateway_port))

        # <- Receiving Connection State response
        data_recv, addr = self.sock.recvfrom(1024)
        state_resp_object = knxnet.decode_frame(data_recv)
        return state_resp_object

    def connection_request(self):
        print('#1 Connection request')
        conn_req_object = \
            knxnet.create_frame(knxnet.ServiceTypeDescriptor.CONNECTION_REQUEST,
                                self.control_endpoint, self.data_endpoint)
        conn_req_dtgrm = conn_req_object.frame  # -> Serializing
        self.sock.sendto(conn_req_dtgrm, (self.gateway_ip, self.gateway_port))

        # <- Receiving Connection response
        data_recv, addr = self.sock.recvfrom(1024)
        conn_resp_object = knxnet.decode_frame(data_recv)
        return conn_resp_object


def process(argv):
    data = int(argv[0])
    size = int(argv[1])
    apci = int(argv[2])
    grp_add = argv[3]

    print(grp_add[0])

    print('data: ', argv[0])
    print('size: ', argv[1])
    print('acpi: ', argv[2])
    print('group: ', argv[3])

    dest_addr_group = knxnet.GroupAddress.from_str(grp_add)

    c1 = connectionKNX("127.0.0.1", 3671)

    # set action
    c1.action = grp_add[0]

    if c1.action < '4':
        c1.send_data(data, size, apci, dest_addr_group)

    else:
        data = c1.read_data(data, size, apci, dest_addr_group)
        print('The value is :', data)


if __name__ == "__main__":
    # run in terminal with 'python3 KNX.py arg1 arg2 arg3 arg4'
    process(sys.argv[1:])
