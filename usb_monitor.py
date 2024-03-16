import usb.core
import pyudev
import argparse
import yaml
import os.path


# Define the authorized USB devices IDs
device_whitelist = []

# Is the device whitelisted ?
def is_authorized(device):
    for elem in device_whitelist:
        if device.idVendor == elem['idVendor'] and device.idProduct == elem['idProduct']:
            return True
    return False

# Through PyUDEV, check if the device is a physical device or just an interface
def pyudev_is_main_device(device):
    return 'BUSNUM' in device and 'DEVNUM' in device

# Detach the interface
def detach(device, interface):
    if device.is_kernel_driver_active(interface.bInterfaceNumber):
        device.detach_kernel_driver(interface.bInterfaceNumber)

# Get rid of all the unauthorized interfaces
def detach_all(device):
    for config in device:
        for interface in config:
                detach(device, interface)

# Print some relevant data about the device
def print_device_info(device):
    print("Device info:")
    print(f"    Manufacturer: {device.manufacturer}")
    print(f"    Product: {device.product}")
    print(f"    IDVendorID: {hex(device.idVendor)}")
    print(f"    IDModelID: {hex(device.idProduct)}")

# Check the devices plugged before the monitor started
def check_initial_devices(enforcing_mode, device_whitelist):
    devices = usb.core.find(find_all=True)

    # Check each device
    for device in devices:
        if device is not None:
            if is_authorized(device):
                # This device is OK to use, do nothing
                print("Authorized device was already connected.")
                print_device_info(device)
            # The device is not whitelisted. Get, him, out. 
            else:
                print("Unauthorized device was already connected.")
                print_device_info(device)
                if enforcing_mode:
                    detach_all(device)
                    print("Unauthorized device connection has been terminated.")

# Whitelist the initial devices
def whitelist_initial_devices():
    devices = usb.core.find(find_all=True)
    # Check each device
    for device in devices:
        if device is not None:
            if not is_authorized(device):
                device_whitelist.append({'idVendor': device.idVendor, 'idProduct': device.idProduct})
                print("Whitelisted an initial device.")
                print_device_info(device)

# The monitoring function, checks for new devices plugged in and handles them
def monitor_usb(enforcing_mode, device_whitelist):
    # Create pyudev context and monitor
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb')

    # Continuously monitor USB events
    for action, device in monitor:
        if device.action == 'add' and pyudev_is_main_device(device):
            # Now that we have the device in PyUDEV, try to get it from PyUSB
            print(f"USB device connected: {device.get('ID_VENDOR_ID')}:{device.get('ID_MODEL_ID')}")
            found_id_vendor = int(device.get('ID_VENDOR_ID'), 16)
            found_id_product = int(device.get('ID_MODEL_ID'),  16)
            usb_device = usb.core.find(idVendor=found_id_vendor, idProduct=found_id_product)
            # Check if we actually found a match
            if usb_device is not None:
                # Check if it is authorized
                if is_authorized(usb_device):
                    print("Authorized device detected.")
                    print_device_info(usb_device)
                # If unauthorized and we are enforcing the rules, kick em where it hurts
                else:
                    print("Unauthorized device detected.")
                    print_device_info(usb_device)
                    if enforcing_mode:
                        detach_all(usb_device)
                        print("Unauthorized device connection has been terminated.")
            else:
                print("A USB device has been detected by the monitor but could not be retrieved properly.")

# Parses the arguments of the program
def parse_args():
    # Parse CLI arguments
    parser = argparse.ArgumentParser(description="USB device monitoring and enforcement program")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-e", "--enforce", action="store_true", help="Enable enforcing mode")
    group.add_argument("-m", "--monitor", action="store_true", help="Enable monitoring mode")
    return parser.parse_args()

# Parses the config file
def parse_config_file(config_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

# How the program goes about it's thing according to the config and the arguments
def main():
    # Get the paths to the config file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(script_dir, "config.yaml")

    # Read the args and the config file
    args = parse_args()
    config = parse_config_file(config_file_path)

    # Setup the whitelist
    conf_whitelist = config.get("device_whitelist", [])
    if conf_whitelist is not None:
        for device in conf_whitelist:
            device_whitelist.append(device)
    if config.get("all_initial_devices_are_safe"):
        whitelist_initial_devices()

    # Prioritize the arguments
    if args.enforce:
        print("Enforcing mode enabled. Unauthorized devices will be disconnected.")
        enforcing_mode = True
    elif args.monitor:
        print("Monitoring mode enabled.")
        enforcing_mode = False
    else:
        enforcing_mode = config.get("default_enforcing_mode", False)
        print("Selected the default enforcing mode:", enforcing_mode)

    # Devices plugged before the monitoring started ?
    if config.get("check_initial_devices", False):
        check_initial_devices(enforcing_mode, device_whitelist)

    # Start monitoring
    monitor_usb(enforcing_mode, device_whitelist)

if __name__ == "__main__":
    main()