import re
import unittest


REQUEST = '#'
REPLY = '*'

ACTION = 'A'
QUERY = 'Q'
CONFIG = 'C'

LssCommandDescription = {
    'ID': 'Device ID',
    'B': 'Baudrate',
    'D': 'Position in Degrees',
    'DT': 'Position in Degrees',
    'MD': 'Move in Degrees',
    'WD': 'Wheel mode in Degrees',
    'VT': 'Wheel mode in Degrees',
    'WR': 'Wheel mode in RPM',
    'P': 'Position in PWM',
    'M': 'Move in PWM (relative)',
    'RDM': 'Raw Duty-Cycle Move',
    'Q': 'Query Status',
    'L': 'Limp',
    'H': 'Halt & Hold',
    'EM': 'Enable Motion Profile',
    'FPC': 'Filter Position Count',
    'O': 'Origin Offset',
    'AR': 'Angular Range',
    'AS': 'Angular Stiffness',
    'AH': 'Angular Holding Stiffness',
    'AA': 'Angular Acceleration',
    'AD': 'Andular Deceleration',
    'G': 'Gyre Direction',
    'FD': 'First Position',
    'MMD': 'Maximum Motor Duty',
    'S': 'Query Speed',
    'SD': 'Maximum Speed in Degrees',
    'SR': 'Maximum Speed in RPM',
    'V': 'Voltage',
    'T': 'Temperature',
    'C': 'Current (Amps)',
    'LED': 'LED Color',
    'LB': 'LED Blinking',
    'MS': 'Model String',
    'F': 'Firmware',
    'N': 'Serial Number'
}

LssCommandModifier = {
    'S': 'Speed',
    'SD': 'Speed in Degrees',
    'T': 'Timed Move',
    'CH': 'Current Hold',
    'CL': 'Current Limp'
}

packet_re = re.compile('(#|\\*)(\\d+)(Q|C)?([a-z]*)([0-9-]+)?([a-z0-9\\-.]*)?', re.IGNORECASE)


class LssException(Exception):
    def __init__(self, message: str):
        self.message = message


class LssPacket(object):

    id: int
    direction: REQUEST or REPLY
    kind: ACTION or QUERY or CONFIG

    command: str
    description: str
    value: int or float or str

    known: bool

    def __init__(self, packet: str):
        self.parse(packet)

    def parse(self, packet: str):
        m = packet_re.match(packet)
        if m:
            self.direction = m[1]
            self.id = int(m[2])
            self.kind = m[3] if m[3] is not None else ACTION
            self.command = m[4]
            self.value = None
            extra = m[6]
            if self.kind == QUERY and self.command == '':
                # the lonely Q command for query status
                self.command = 'Q'
            if m[5]:
                if m[5] == '-':
                    # only minus matched, this is not an integer value
                    extra = m[5] + extra
                else:
                    self.value = int(m[5])
            # possibly we have a string command
            # m[6] may have a continuation of the response
            if len(extra) > 0:
                if self.direction == REPLY and self.kind == QUERY:
                    if self.command.startswith('MS'):
                        self.value = self.command[2:] + extra
                        self.command = 'MS'
                    elif self.command.startswith('F'):
                        self.value = self.command[1:] + extra
                        self.command = 'F'
                    elif self.command.startswith('N'):
                        self.value = self.command[1:] + extra
                        self.command = 'N'
                    elif extra is not None:
                        # garbage value after command
                        raise LssException('Garbled packet value')
                else:
                    self.value = None

            if self.command in LssCommandDescription:
                self.description = LssCommandDescription[self.command]
                self.known = True
            else:
                self.description = 'Unknown command'
                self.known = False
        else:
            raise LssException('Invalid packet')


class LssPacketTests(unittest.TestCase):
    def assert_packet(self, p: LssPacket):
        self.assertIsNotNone(p)
        self.assertGreater(p.id, 0)
        self.assertLess(p.id, 50)
        self.assertIn(p.direction, [REQUEST, REPLY])
        self.assertIn(p.kind, [ACTION, QUERY, CONFIG])
        self.assertTrue(p.known)

    def test_command_position(self):
        self.assert_packet(LssPacket('#12D521'))

    def test_reply_model(self):
        p = LssPacket('*12QMSLSS-HT1')
        self.assert_packet(p)
        self.assertEqual(p.value, 'LSS-HT1')

    def test_reply_position(self):
        p = LssPacket('*12QD980')
        self.assert_packet(p)
        self.assertEqual(p.value, 980)

    def test_reply_neg_position(self):
        p = LssPacket('*19QD-1190')
        self.assert_packet(p)
        self.assertEqual(p.value, -1190)

    def test_reply_QS0(self):
        p = LssPacket('*19QS900')
        self.assert_packet(p)
        self.assertEqual(p.value, 900)

if __name__ == '__main__':
    unittest.main()
