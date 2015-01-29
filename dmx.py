import random
import datetime
from USBIP import BaseStucture, USBDevice, InterfaceDescriptor, DeviceConfigurations, EndPoint, USBContainer

# Emulating FTDI FT232 USB-serial converter

interface_d = InterfaceDescriptor(
    bAlternateSetting=0,
    bNumEndpoints=2,
    bInterfaceClass=255,
    bInterfaceSubClass=255,
    bInterfaceProtocol=255,
    iInterface=2
)

interface_d.endpoints = [
    EndPoint(
        bEndpointAddress=0x81,
        bmAttributes=0x02,
        wMaxPacketSize=0x4000,
        bInterval=0
    ),
    EndPoint(
        bEndpointAddress=0x02,
        bmAttributes=0x3,
        wMaxPacketSize=0x4000,
        bInterval=0
    )
]

configuration = DeviceConfigurations(
    wTotalLength=0x2000,
    bNumInterfaces=1,
    bConfigurationValue=1,
    iConfiguration=0,
    bmAttributes=0xa0,
    bMaxPower=45
)

configuration.interfaces = [interface_d]

class FTDIDevice(USBDevice):
    vendorID = 0x0403
    productID = 0x6001
    bcdDevice = 0x0600
    bNumConfigurations = 0x1
    bNumInterfaces = 0x1
    bConfigurationValue = 0x1
    bDeviceClass = 0x0
    bDeviceSubClass = 0x0
    bDeviceProtocol = 0x0
    iManufacturer = 0
    iProduct = 2
    iSerial = 0
    configurations = [configuration]

    def __init__(self):
        USBDevice.__init__(self)

dev = FTDIDevice()
usb_container = USBContainer()
usb_container.add_usb_device(dev)
usb_container.run()
