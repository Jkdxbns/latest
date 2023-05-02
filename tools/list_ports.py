import os

if os.name == 'nt':  # sys.platform == 'win32':
    from serial.tools.list_ports_windows import comports
else:
    raise ImportError("Sorry: no implementation for your platform ('{}') available".format(os.name))


def main():
    hits = 0
    comPortList = []
    iterator = sorted(comports(True))

    for n, (port, desc, hwid) in enumerate(iterator, 1):
        portName = "{}".format(port)
        # sys.stdout.write(portName)
        comPortList.append(portName)
        hits += 1

    if hits == 0:
        # sys.stderr.write("no ports found\n")
        print("No ports found.")
        return
    return comPortList
