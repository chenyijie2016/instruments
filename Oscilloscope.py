from .instrument import VISAInstrument

MeasureType = {'vrms', 'vpp', 'vmax', 'vmin', 'vamplitude', 'vaverage', 'vbase', 'vtop', 'vupper', 'vmiddle', }


class Oscilloscope(VISAInstrument):
    def __init__(self, usb_visa_address):
        instrument_name = 'Oscilloscope'
        super().__init__(usb_visa_address, instrument_name)
        self.system = self.System(self)
        self.channel = self.Channel(self)
        self.trigger = self.Trigger(self)
        self.measure = self.Measure(self)


    class System:
        def __init__(self, outer):
            self.outer = outer

        def preset(self):
            self.outer.do_command(':system:preset')

    class Channel:
        def __init__(self, outer):
            self.outer = outer

        def set_coupling(self, n, coupling):
            self.outer.do_command(f':channel{n}:coupling {coupling}')

        def get_coupling(self, n):
            self.outer.do_command(f':channel{n}:coupling')

        def set_scale(self, n: int, scale: float):
            self.outer.do_command(f':channel{n}:scale {scale}')

        def get_scale(self, n: int):
            return self.outer.query_number(f':channel{n}:scale?')

        def set_display(self, n, value):
            self.outer.do_command(f':channel{n}:display {value}')

        def get_display(self, n: int):
            return self.outer.query_string(f':channel{n}:display?')



    class Trigger:
        def __init__(self, outer):
            self.outer = outer

        def set_level_as_setup(self):
            self.outer.do_command(f':trigger:level:asetup')

        def set_mode(self, mode):
            self.outer.do_command(f':trigger:mode {mode}')

        def get_mode(self):
            return self.outer.query_string(f':trigger:mode?')

        def set_edge_source(self, source):
            self.outer.do_command(f':trigger:edge:source {source}')

        def get_edge_source(self):
            return self.outer.query_string(f':trigger:edge:source?')

    class Measure:
        def __init__(self, outer):
            self.outer = outer
        # VRMS
        def get_voltage_root_mean_square(self, interval='display', type='DC', source='channel1'):
            return self.outer.do_query_number(f':measure:vrms? {interval},{type},{source}')

        def add_voltage_root_mean_square(self, interval='display', type='DC', source='channel1'):
            self.outer.do_command(f':measure:vrms {interval},{type},{source}')

        # Frequency
        def get_frequency(self,  source='channel1'):
            return self.outer.query_number(f':measure:frequency? {source}')

        def add_frequency(self, source='channel1'):
            self.outer.do_command(f':measure:frequency {source}')

        # VMAX
        def get_voltage_max(self, source='channel1'):
            return self.outer.do_query_number(f':measure:vmax? {source}')

        def add_voltage_max(self, source='channel1'):
            self.outer.do_command(f':measure:vmax {source}')

        # VMIN
        def get_voltage_min(self, source='channel1'):
            return self.outer.do_query_number(f':measure:vmin? {source}')

        def add_voltage_min(self, source='channel1'):
            self.outer.do_command(f':measure:vmin {source}')

    class TimeBase:
        def __init__(self, outer):
            self.outer = outer

    def set_timebase(self, timebase):
        self.write(f':timebase:scale {timebase}')
