import socket
import struct
import time
import threading

class BaseStructure:
    _format_prefix = '>'

    def __init__(self, **kwargs):
        for field in self._fields_:
            if len(field) > 2:
                setattr(self, field[0], field[2])
        for key, value in kwargs.items():
            setattr(self, key, value)

    def size(self):
        return struct.calcsize(self.format())

    def format(self):
        pack_format = self._format_prefix
        for field in self._fields_:
            if isinstance(field[1], str):
                pack_format += field[1]
            else:
                pack_format += str(field[1]().size()) + 's'
        return pack_format

    def pack(self):
        values = []
        for field in self._fields_:
            if isinstance(field[1], str):
                values.append(getattr(self, field[0], 0))
            else:
                 values.append(getattr(self, field[0], field[1]()).pack())
        return struct.pack(self.format(), *values)

    def unpack(self, buf):
        values = struct.unpack(self.format(), buf)
        for field, value in zip(self._fields_, values):
            if isinstance(field[1], str):
                setattr(self, field[0], value)
            else:
                v = field[1]()
                v.unpack(value)
                setattr(self, field[0], v)

    def __str__(self):
        s = '{'
        for field in self._fields_:
            s += field[0] + ': ' + str(getattr(self, field[0], 0)) + ', '
        s += '}'
        return s


# Standard USB structures

class USBSetupPacket(BaseStructure):
    _format_prefix = '<'
    _fields_ = [
        ('bmRequestType', 'B'),
        ('bRequest', 'B'),
        ('wValue', 'H'),
        ('wIndex', 'H'),
        ('wLength', 'H')
    ]

class DeviceDescriptor(BaseStructure):
    _format_prefix = '<'
    _fields_ = [
        ('bLength', 'B', 18),
        ('bDescriptorType', 'B', 1),
        ('bcdUSB', 'H', 0x0110),
        ('bDeviceClass', 'B'),
        ('bDeviceSubClass', 'B'),
        ('bDeviceProtocol', 'B'),
        ('bMaxPacketSize0', 'B'),
        ('idVendor', 'H'),
        ('idProduct', 'H'),
        ('bcdDevice', 'H'),
        ('iManufacturer', 'B'),
        ('iProduct', 'B'),
        ('iSerialNumber', 'B'),
        ('bNumConfigurations', 'B')
    ]


class DeviceConfigurations(BaseStructure):
    _format_prefix = '<'
    _fields_ = [
        ('bLength', 'B', 9),
        ('bDescriptorType', 'B', 2),
        ('wTotalLength', 'H', 0x2200),
        ('bNumInterfaces', 'B', 1),
        ('bConfigurationValue', 'B', 1),
        ('iConfiguration', 'B', 0),
        ('bmAttributes', 'B', 0x80),
        ('bMaxPower', 'B', 0x32)
    ]


class InterfaceDescriptor(BaseStructure):
    _format_prefix = '<'
    _fields_ = [
        ('bLength', 'B', 9),
        ('bDescriptorType', 'B', 4),
        ('bInterfaceNumber', 'B', 0),
        ('bAlternateSetting', 'B', 0),
        ('bNumEndpoints', 'B', 1),
        ('bInterfaceClass', 'B', 3),
        ('bInterfaceSubClass', 'B', 1),
        ('bInterfaceProtocol', 'B', 2),
        ('iInterface', 'B', 0)
    ]

class EndPoint(BaseStructure):
    _format_prefix = '<'
    _fields_ = [
        ('bLength', 'B', 7),
        ('bDescriptorType', 'B', 0x5),
        ('bEndpointAddress', 'B', 0x81),
        ('bmAttributes', 'B', 0x2),
        ('wMaxPacketSize', 'H', 0x8000),
        ('bInterval', 'B', 0x0A)
    ]

# USBIP structures

class USBIPHeader(BaseStructure):
    _fields_ = [
        ('version', 'H', 0x0111),
        ('command', 'H'),
        ('status', 'I')
    ]

class USBInterface(BaseStructure):
    _fields_ = [
        ('bInterfaceClass', 'B'),
        ('bInterfaceSubClass', 'B'),
        ('bInterfaceProtocol', 'B'),
        ('align', 'B', 0)
    ]

class OPREPDevList(BaseStructure):
    _fields_ = [
        ('base', USBIPHeader),
        ('nExportedDevice', 'I'),
        ('usbPath', '256s'),
        ('busID', '32s'),
        ('busnum', 'I'),
        ('devnum', 'I'),
        ('speed', 'I'),
        ('idVendor', 'H'),
        ('idProduct', 'H'),
        ('bcdDevice', 'H'),
        ('bDeviceClass', 'B'),
        ('bDeviceSubClass', 'B'),
        ('bDeviceProtocol', 'B'),
        ('bConfigurationValue', 'B'),
        ('bNumConfigurations', 'B'),
        ('bNumInterfaces', 'B'),
        ('interfaces', USBInterface)
    ]

class OPREPImport(BaseStructure):
    _fields_ = [
        ('base', USBIPHeader),
        ('usbPath', '256s'),
        ('busID', '32s'),
        ('busnum', 'I'),
        ('devnum', 'I'),
        ('speed', 'I'),
        ('idVendor', 'H'),
        ('idProduct', 'H'),
        ('bcdDevice', 'H'),
        ('bDeviceClass', 'B'),
        ('bDeviceSubClass', 'B'),
        ('bDeviceProtocol', 'B'),
        ('bConfigurationValue', 'B'),
        ('bNumConfigurations', 'B'),
        ('bNumInterfaces', 'B')
    ]

class USBIPRETSubmit(BaseStructure):
    _fields_ = [
        ('command', 'I'),
        ('seqnum', 'I'),
        ('devid', 'I'),
        ('direction', 'I'),
        ('ep', 'I'),
        ('status', 'I'),
        ('actual_length', 'I'),
        ('start_frame', 'I'),
        ('number_of_packets', 'I'),
        ('error_count', 'I'),
        ('setup', USBSetupPacket)
    ]

class USBIPCMDSubmit(BaseStructure):
    _fields_ = [
        ('command', 'I'),
        ('seqnum', 'I'),
        ('devid', 'I'),
        ('direction', 'I'),
        ('ep', 'I'),
        ('transfer_flags', 'I'),
        ('transfer_buffer_length', 'I'),
        ('start_frame', 'I'),
        ('number_of_packets', 'I'),
        ('interval', 'I'),
        ('setup', USBSetupPacket)
    ]

def string_descriptor(s):
    encoded = s.encode('utf-16le')
    assert(len(encoded) < 0xfe)
    l = chr(len(encoded) + 2)
    return l + '\x03' + encoded

class USBServer():
    # configuration + interface + endpoints
    device_descriptor = \
        DeviceDescriptor(
            bDeviceClass = 0,
            bDeviceSubClass = 0,
            bDeviceProtocol = 0,
            bMaxPacketSize0 = 8,
            idVendor = 0x0403,
            idProduct = 0x6001,
            bcdDevice = 0x0600,
            iManufacturer = 1,
            iProduct = 2,
            iSerialNumber = 3,
            bNumConfigurations = 1
        )

    configuration_descriptor = \
        DeviceConfigurations(
            wTotalLength = 32,
            bNumInterfaces = 1,
            bConfigurationValue = 1,
            iConfiguration = 0,
            bmAttributes = 0xa0,
            bMaxPower = 45
        )

    interface_descriptor = \
        InterfaceDescriptor(
            bAlternateSetting = 0,
            bNumEndpoints = 2,
            bInterfaceClass = 255,
            bInterfaceSubClass = 255,
            bInterfaceProtocol = 255,
            iInterface = 2
        )

    configuration_descriptor_string = \
        configuration_descriptor.pack() + \
        interface_descriptor.pack() + \
        EndPoint(
            bEndpointAddress = 0x81,
            bmAttributes = 0x02,
            wMaxPacketSize = 64,
            bInterval = 0
        ).pack() + \
        EndPoint(
            bEndpointAddress = 0x02,
            bmAttributes = 0x02,
            wMaxPacketSize = 64,
            bInterval = 0
        ).pack()

    def send_usb_req(self, usb_req, usb_res, status=0):
        self.connection.sendall(
            USBIPRETSubmit(
                command = 0x3,
                seqnum = usb_req.seqnum,
                ep = 0,
                status = status,
                actual_length = len(usb_res),
                start_frame = 0x0,
                number_of_packets = 0x0,
                interval = 0x0
            ).pack() + usb_res)

    def handle_get_descriptor(self, setup, usb_req):
        handled = False
        if setup.wValue == 0x0100: # Device
            print 'Get Device Descriptor'
            handled = True
            self.send_usb_req(usb_req, self.device_descriptor.pack())
        elif setup.wValue == 0x0200: # configuration
            print 'Get Configuration Descriptor'
            handled = True
            self.send_usb_req(usb_req, self.configuration_descriptor_string)
        elif setup.wValue == 0x0300: # string
            print 'Get String Descriptor 0'
            handled = True
            self.send_usb_req(usb_req, '\x04\x03\x09\x04')
        elif setup.wValue == 0x0301: # string
            print 'Get String Descriptor 1'
            handled = True
            self.send_usb_req(usb_req, string_descriptor('FTDI'))
        elif setup.wValue == 0x0302: # string
            print 'Get String Descriptor 2'
            handled = True
            self.send_usb_req(usb_req, string_descriptor('FT232R USB UART'))
        elif setup.wValue == 0x0303: # string
            print 'Get String Descriptor 3'
            handled = True
            self.send_usb_req(usb_req, string_descriptor('A900DGX9'))
        return handled

    def handle_usb_control(self, req):
        handled = False
        if req.setup.bmRequestType == 0x80: # Host Request
            if req.setup.bRequest == 0x6: # Get Descriptor
                handled = self.handle_get_descriptor(req.setup, req)
            if req.setup.bRequest == 0x0: # Get Status
                print 'Get Status'
                self.send_usb_req(req, '\x00\x00')
                handled = True
        elif req.setup.bmRequestType == 0x00:
            if req.setup.bRequest == 0x9: # Set Configuration
                print 'Set Configuration'
                self.send_usb_req(req, '')
                handled = True
        elif req.setup.bmRequestType == 0xc0:
            if req.setup.bRequest == 0x90: # ?
                print 'First ignored request type'
                self.send_usb_req(req, '')
                handled = True
        if not handled:
            if req.direction == 0:
                print 'Unknown control write'
                self.send_usb_req(req, '')
            else:
                print 'Unknown control read'
                print(req)
                self.send_usb_req(req, '\x00')

    def empty_reply_later(self, usb_req):
        # I'm hoping the GIL protects me from multiple threads accessing the socket at once
        def target():
            time.sleep(1)
            self.send_usb_req(usb_req, '')
        threading.Thread(target=target).start()

    def handle_usb_request(self, usb_req):
        if usb_req.ep == 0:
            self.handle_usb_control(usb_req)
        elif usb_req.ep == 1:
            print('Read data')
            self.empty_reply_later(usb_req)
        elif usb_req.ep == 2:
            # The host is sending data
            # Read it
            l = self.connection.recv(usb_req.transfer_buffer_length)
            assert(len(l) == usb_req.transfer_buffer_length)
            print('DATA: %s'%repr(l))
            self.send_usb_req(usb_req, '')
        else:
            assert(False)

    def handle_attach(self):
        return OPREPImport(
            base = USBIPHeader(command = 3, status = 0),
            usbPath = '/sys/devices/pci0000:00/0000:00:01.2/usb1/1-1',
            busID = '1-1',
            busnum = 1,
            devnum = 2,
            speed = 2,
            idVendor = self.device_descriptor.idVendor,
            idProduct = self.device_descriptor.idProduct,
            bcdDevice = self.device_descriptor.bcdDevice,
            bDeviceClass = self.device_descriptor.bDeviceClass,
            bDeviceSubClass = self.device_descriptor.bDeviceSubClass,
            bDeviceProtocol = self.device_descriptor.bDeviceProtocol,
            bNumConfigurations = self.device_descriptor.bNumConfigurations,
            bConfigurationValue  =  self.configuration_descriptor.bConfigurationValue,
            bNumInterfaces = self.configuration_descriptor.bNumInterfaces
        )

    def handle_device_list(self):
        return OPREPDevList(
            base = USBIPHeader(command = 5, status = 0),
            nExportedDevice = 1,
            usbPath = '/sys/devices/pci0000:00/0000:00:01.2/usb1/1-1',
            busID = '1-1',
            busnum = 1,
            devnum = 2,
            speed = 2,
            idVendor = self.device_descriptor.idVendor,
            idProduct = self.device_descriptor.idProduct,
            bcdDevice = self.device_descriptor.bcdDevice,
            bDeviceClass = self.device_descriptor.bDeviceClass,
            bDeviceSubClass = self.device_descriptor.bDeviceSubClass,
            bDeviceProtocol = self.device_descriptor.bDeviceProtocol,
            bNumConfigurations = self.device_descriptor.bNumConfigurations,
            bConfigurationValue  =  self.configuration_descriptor.bConfigurationValue,
            bNumInterfaces = self.configuration_descriptor.bNumInterfaces,
            interfaces = USBInterface(
                bInterfaceClass = self.interface_descriptor.bInterfaceClass,
                bInterfaceSubClass = self.interface_descriptor.bInterfaceSubClass,
                bInterfaceProtocol = self.interface_descriptor.bInterfaceProtocol
            )
        )

    def run(self, ip='0.0.0.0', port=3240):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((ip, port))
        s.listen(5)
        attached = False
        while 1:
            print 'Listening for connection on %s:%d' % (ip, port)
            conn, addr = s.accept()
            print 'Received connection from %s:%d' % addr
            while 1:
                if not attached:
                    req = USBIPHeader()
                    data = conn.recv(req.size())
                    if not data:
                        break
                    req.unpack(data)
                    if req.command == 0x8005:
                        print 'List devices'
                        conn.sendall(self.handle_device_list().pack())
                    elif req.command == 0x8003:
                        print 'Attach device'
                        conn.recv(32)  # receive bus id
                        conn.sendall(self.handle_attach().pack())
                        attached = True
                    else:
                        print 'Unknown command: %04x' % (req.command,)
                        assert(False)
                else:
                    cmd = USBIPCMDSubmit()
                    data = conn.recv(cmd.size())
                    cmd.unpack(data)
                    assert(cmd.command == 1)
                    self.connection = conn
                    self.handle_usb_request(cmd)
            print 'Closing connection'
            conn.close()

USBServer().run()
