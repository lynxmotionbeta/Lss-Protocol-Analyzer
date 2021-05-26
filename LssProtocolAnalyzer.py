# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting
from lss import LssPacket, LssException, REQUEST, REPLY, QUERY, ACTION, CONFIG

# High level analyzers must subclass the HighLevelAnalyzer class.
class LssHLA(HighLevelAnalyzer):
    packet_start: float
    packet: str or None

    # List of settings that a user can set for this High Level Analyzer.
    #my_string_setting = StringSetting()
    #my_number_setting = NumberSetting(min_value=0, max_value=100)
    DisplayLevel = ChoicesSetting(
        label='Display Level',
        choices=('All', 'Errors Only')
    )

    # An optional list of types this analyzer produces, providing a way to customize the way frames are displayed in Logic 2.
    result_types = {
        'request': {
            'format': '{{data.description}}'
        },
        'reply': {
            'format': '{{data.description}}'
        },
        'error': {
            'format': '!! {{data.description}}'
        }
    }

    def __init__(self):
        '''
        Initialize HLA.

        Settings can be accessed using the same name used above.
        '''
        self.packet_start = 0
        self.packet_type = 'Command'
        self.packet_error = False
        self.packet = None


    @staticmethod
    def action_name(a):
        if a == QUERY:
            return 'Query'
        elif a == CONFIG:
            return 'Config'
        elif a == ACTION:
            return 'Action'
        else:
            return '?'


    def decode(self, frame: AnalyzerFrame):
        '''
        Process a frame from the input analyzer, and optionally return a single `AnalyzerFrame` or a list of `AnalyzerFrame`s.

        The type and data values in `frame` will depend on the input analyzer.
        '''
        try:
            ch = frame.data['data'].decode('ascii')
        except:
            # Not an ASCII character
            return

        if ch == '\r':
            try:
                parsed = LssPacket(self.packet)
                error = not parsed.known
                type = 'request' if parsed.direction == REQUEST else 'reply'

                # this is the end of the packet
                frame = AnalyzerFrame(
                    type if parsed.known else 'error',
                    self.packet_start,
                    frame.end_time, {
                        'id': str(parsed.id),
                        'kind': LssHLA.action_name(parsed.kind),
                        'command': parsed.description,
                        'value': str(parsed.value),
                        'bytes': self.packet,
                        'description': parsed.description
                })
            except LssException as e:
                error = True

                # exception frame
                frame = AnalyzerFrame(
                    'error',
                    self.packet_start,
                    frame.end_time, {
                        'kind': '?',
                        'bytes': self.packet,
                        'description': e.message
                })

            self.packet_start = 0
            self.packet_error = False
            self.packet = None

            # return a valid LSS packet frame
            return frame if error or self.DisplayLevel == 'All' else None
        else:
            if self.packet is None:
                self.packet = ch
                self.packet_start = frame.start_time
            else:
                self.packet += ch

        return
