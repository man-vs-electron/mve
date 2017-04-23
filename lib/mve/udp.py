import socket
import struct
import sys
import threading
import time
from mve.utils import eprint

def register(component_name, multicast_ip='224.3.29.71', multicast_port=10000):
    """Discovers and registers with a UDP Server

    Returns the IP address of the server.  This
    function issues a message over UDP multicast
    and looks for a response.  The message is in
    the form of "register:component_name".  

    Arguments:
    component_name -- The name of the thing registering
    """    
    message = 'register:%s' % component_name
    multicast_group = (multicast_ip, multicast_port)

    # Create the datagram socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set a timeout so the socket does not block indefinitely when trying
    # to receive data.
    sock.settimeout(0.2)

    # Set the time-to-live for messages to 1 so they do not go past the
    # local network segment.
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    try:

    
    # Look for responses from all recipients
        while True:
            # Send data to the multicast group
            eprint('sending "%s"' % message)
            sent = sock.sendto(message, multicast_group)            
            eprint('waiting to receive')
            try:
                data, server = sock.recvfrom(16)
                if data.startswith("monitor"):
                    eprint("Found the monitor on %s" % (str(server)))
                return server[0]
            except socket.timeout:
                eprint('timed out, still waiting')
                time.sleep(2)
            else:
                eprint('received "%s" from %s' % (data, server))
            
    finally:
        eprint('closing socket')
        sock.close()


def udp_server(callback, multicast_ip='224.3.29.71', server_port=10000):
    """Listens and responds to UPD registration messages

    This function opens a UDP multicast server and listen.
    When it receives a message, it passage it to callback.
    If callback returns something other than None, it sends
    that response out.
    
    Arguments:
    callback -- the callback for determining responses, takes the form (data, address)
    multicast_ip -- the ip for the multicast group (default='224.3.29.71')
    server_port -- the server port for the multicast (default=10000)
    """
    multicast_group = multicast_ip
    server_address = ('', server_port)

    # Create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind to the server address
    sock.bind(server_address)

    # Tell the operating system to add the socket to the multicast group
    # on all interfaces.
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # Receive/respond loop
    while True:
        eprint('\nwaiting to receive message')
        data, address = sock.recvfrom(1024)

        if data.startswith("register:"):
            eprint('received %s bytes from %s' % (len(data), address[0]))
            eprint(data)

            eprint('sending acknowledgement to', address)

            response = callback(data, address)
            
            sock.sendto(response, address)

        else:
           eprint('received invalid data (%s) from %s' % (data, address[0]))

def start_udp_server(callback, isDaemon=True, multicast_ip='224.3.29.71', server_port=10000):
    """Start the DDP server on a separate thread

    Arguments:
    callback -- function in the form of (data, sender) to determine responses
    isDaemon -- whether python should exit if this is the only thread left
    multicast_ip -- the ip for the multicast group (default='224.3.29.71')
    server_port -- the server port for the multicast (default=10000)
    """
    t = threading.Thread(target=udp_server, args=(callback, multicast_ip, server_port))
    t.setDaemon(isDaemon)
    t.start()
    return t
