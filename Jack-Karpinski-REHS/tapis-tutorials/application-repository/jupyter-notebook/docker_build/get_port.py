import argparse

# FRONTERA
START_CHASSIS = 0
END_CHASSIS = 21

START_NODE = 1
END_NODE = 4

TOTAL_CHASSIS = END_CHASSIS - START_CHASSIS + 1
TOTAL_NODES = END_NODE - START_NODE + 1


def get_port(start_port, rack, chassis, node):
    port = (TOTAL_CHASSIS * TOTAL_NODES) * (rack - 1) + (TOTAL_NODES * chassis) + node + (start_port - 1)
    if port > 65535:
        raise OverflowError('Starting port is too large and resulting port is out of bounds!\n'
                            f'Desired port: {port}\n'
                            'Max port: 65535')
    return port


parser = argparse.ArgumentParser()
parser.add_argument('start_port', metavar='STARTPORT', type=int, help='Port number range starts here')
parser.add_argument('compute_node', metavar='COMPUTENODE', type=str, help='Compute node formatted as c###-###')
args = parser.parse_args()

# c1RR-CCN: 1 (frontera racks all start with 1), R (rack), C (chassis), N (node)
try:
    rack = int(args.compute_node[2:4])
    chassis = int(args.compute_node[5:7])
    node = int(args.compute_node[7:])
except Exception:
    print('ERROR: Cannot parse invalid compute_node value')
finally:
    print(get_port(args.start_port, rack, chassis, node))