"""
ZeroMQ Twisted factory which is controlling ZeroMQ context.

Copyright (c) 2014 Samsung Electronics Co., Ltd.
"""
from zmq import Context

from twisted.internet import reactor


class ZmqContextManager(object):
    """
    I control individual ZeroMQ connections.

    Factory creates and destroys ZeroMQ context.

    :var reactor: reference to Twisted reactor used by all the connections
    :var ioThreads: number of IO threads ZeroMQ will be using for this context
    :vartype ioThreads: int
    :var lingerPeriod: number of milliseconds to block when closing socket
        (terminating context), when there are some messages pending to be sent
    :vartype lingerPeriod: int

    :var connections: set of instantiated :class:`ZmqConnection`
    :vartype connections: set
    :var context: ZeroMQ context
    """

    reactor = reactor
    ioThreads = 1
    lingerPeriod = 100
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(ZmqContextManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        """
        Constructor.

        Create ZeroMQ context.
        """
        if not self.initialized:
            self.initialized = True
            self.connections = set()
            self.context = Context(self.ioThreads)
            reactor.addSystemEventTrigger('during', 'shutdown', self.shutdown)

    def __repr__(self):
        return "ZmqContextManager(%d threads)" % self.ioThreads

    def shutdown(self):
        """
        Shutdown factory.

        This is shutting down all created connections
        and terminating ZeroMQ context. Also cleans up
        Twisted reactor.
        """
        if not self.initialized:
            return
        self.initialized = False
        for connection in self.connections.copy():
            connection.shutdown()

        self.connections = None
        self.context.term()
        self.context = None