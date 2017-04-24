from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
import struct


class States:
    UPDATE_DATA = 0
    GET_DATA = 1


class RadarProtocol(Protocol, object):
    data_send_format = "h" * 64
    data_receive_format = "h" + data_send_format
    # Format is: a short saying what the packet is about + 64 (32 x y) shorts, 32 for team 1 and 32 for team 2

    def __init__(self, fac):
        super(self.__class__, self).__init__()
        self.fac = fac

    def connectionMade(self):
        print("Received connecton!")

    def dataReceived(self, data):
        data_size = len(str(data))
        option = struct.unpack_from('h', data)
        if option[0] == States.UPDATE_DATA:
            if data_size != 130:
                print("Received update data with fucked up size:", data_size)
                #print(data)
                #return
            self.fac.data = list(struct.unpack(self.data_receive_format, data[:130:]))[1::]
        elif option[0] == States.GET_DATA:
            to_send = struct.pack(self.data_send_format, *self.fac.data)
            self.transport.write(to_send)


class RadarFactory(Factory):
    protocol = RadarProtocol
    data = [0] * 64

    def buildProtocol(self, addr):
        return RadarProtocol(self)

endpoint = TCP4ServerEndpoint(reactor, 8985)
endpoint.listen(RadarFactory())
reactor.run()
