# USB-Whitelist

This is part of a larger project that focuses on implementing an attack and defense strategies.
The simulated attack was using a Raspberry Pi Pico, and the [dbisu/pico-ducky](https://github.com/dbisu/pico-ducky) to turn it into a BadUSB.
This is only the defense section, intended to cover at least the attack mentioned and possibly others.
With this in mind, I implemented a form of *USB Device Whitelisting* to help prevent unauthorized devices from interacting in any way with the computer. Also, this program helps with monitoring every USB device that gets plugged in.

## Dependencies

`Python 3.12.2` was used during the development, as well as some libraries :
- [PyUSB](https://github.com/pyusb/pyusb)
- [PyUDEV](https://github.com/pyudev/pyudev)
- [argparse](https://docs.python.org/3/library/argparse.html)
- [PyYAML](https://github.com/yaml/pyyaml)

## Configuration

There are currently 4 configurable parameters in the `config.yaml` file.
Each of them are explained with examples if needed in the file directly.

- `default_enforcing_mode`: set the default enforcing mode when no arguments are passed to the program.
- `check_initial_devices`: some devices might be plugged in the machine before the monitor is up and running. If you want to check these devices too, you can set it here.
- `all_initial_devices_are_safe`: as said before, some device might be plugged before they get monitored. Do we consider them safe automatically ?
- `device_whitelist`: here, you can define which devices are whitelisted as long as you know their `idVendor` and `idProduct`. You might want to run `lsusb` to get these ids.

## Execution

The execution of the program requires `root`.

The program can be run in 2 different modes from the start.
You can find some help on the expected arguments with:
```sh
python usb_monitor.py -h

usage: usb_monitor.py [-h] [-e | -m]

USB device monitoring and enforcement program

options:
  -h, --help     show this help message and exit
  -e, --enforce  Enable enforcing mode
  -m, --monitor  Enable monitoring mode
```

#### Monitor
To start the program in monitoring mode, you can set the `default_enforcing_mode` to `false` in the config or choose to enable it.

This mode is expected to show the connections of each device, notifying you of their authorization but not taking any action to prevent them from doing anything.
It can be used as a first way of checking what is detected, what should be allowed and what should be dealt with.

#### Enforce
To start the program in enforce mode, you can set the `default_enforcing_mode` to `true` in the config or choose to enable it.

This mode is expected to show the connections of each device just as the monitor mode, but whenever an unauthorized device is detected, it should terminate the connection after printing it's informations.