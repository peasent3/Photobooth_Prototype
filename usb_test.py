import usb1

ctx = usb1.USBContext()

for device in ctx.getDeviceList():
    if device.getVendorID() == 0x054C:
        print("Sony device found")
        print(f"Vendor ID : {device.getVendorID():04X}")
        print(f"Product ID: {device.getProductID():04X}")
        print(f"Product   : {device.getProduct()}")

        for configuration in device.iterConfigurations():
            print(f"\nConfiguration {configuration.getConfigurationValue()}")

            for interface in configuration:
                for setting in interface:
                    print(
                        f"  Interface {setting.getNumber()} "
                        f"Alternate {setting.getAlternateSetting()}"
                    )

                    for endpoint in setting:
                        print(
                            f"    Endpoint 0x{endpoint.getAddress():02X} "
                            f"Attributes: 0x{endpoint.getAttributes():02X} "
                            f"MaxPacket: {endpoint.getMaxPacketSize()}"
                        )