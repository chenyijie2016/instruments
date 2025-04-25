import pyvisa
import logging

from .instrument import VISAInstrument

TraceDataFormat = {
    'mlogarithmic',  # Logarithmic magnitude
    'phase',  # Phase
    'gdelay',  # Group delay
    'slinear',  # Linear magnitude
    'slogarithmic',  # Logarithmic magnitude
    'scomplex',  # Complex
    'smith',  # Smith chart
    'sadmittance',  # Admittance
    'plinear',  #
    'plogarithmic',  #
    'polar',  #
    'mlinear',  #
    'swr',  # Standing wave ratio
    'real',  # Real
    'imaginary',  # Imaginary
    'uphase',  # Unwrapped phase
    'pphase',  # Positive phase
}


# noinspection SpellCheckingInspection
class SiglentVNA(VISAInstrument):
    def __init__(self, usb_visa_address):
        instrument_name = 'Signal VNA'
        super().__init__(usb_visa_address, instrument_name)
        self.markers = self.Marker(self)
        self.sweep = self.Sweep(self)
        self.avg = self.AVGBW(self)
        self.measure = self.Measure(self)
        self.system = self.System(self)
        self.power = self.Power(self)
        self.frequency = self.Frequency(self)
        self.save_recall = self.SaveRcall(self)
        self.format = self.Format(self)
        self.scale = self.Scale(self)

    class System:
        def __init__(self, outer):
            self.outer = outer

        def preset(self):
            self.outer.write(':system:preset')

        def set_display_clock(self, state: bool):
            self.outer.write(f':display:clock {int(state)}')

        def get_display_clock(self):
            return self.outer.query(':display:clock?')

    class AVGBW:
        def __init__(self, outer):
            self.outer = outer

        def get_state(self, cnum):
            return self.outer.query(f':sense{cnum}:average:state?')

        def set_state(self, cnum, state: bool):
            self.outer.write(f':sense{cnum}:average:state {int(state)}')

        def set_count(self, cnum, count: int):
            self.outer.write(f':sense{cnum}:average:count {count}')

        def get_count(self, cnum):
            return self.outer.query(f':sense{cnum}:average:count?')

        def get_current(self, cnum):
            return int(self.outer.query(f':sense{cnum}:average:count?'))

        def complete(self, cnum) -> int:
            return int(self.outer.query(f':sense{cnum}:average:complete?'))

        def clear(self, cnum):
            self.outer.write(f':sense{cnum}:average:clear')

    class Sweep:
        SweepType = {'linear', 'logarithmic', 'segment', 'power', 'cw'}

        def __init__(self, outer):
            self.outer = outer

        def get_points(self, cnum):
            return self.outer.query(f':sense{cnum}:sweep:points?')

        def set_points(self, cnum, points: int):
            self.outer.write(f':sense{cnum}:sweep:points {points}')

        def set_type(self, cnum, sweep_type: str):
            assert sweep_type.lower() in self.SweepType
            self.outer.write(f':sense{cnum}:sweep:type {sweep_type}')

        def get_type(self, cnum):
            return self.outer.query(f':sense{cnum}:sweep:type?')

        def set_time_auto(self, cnum, state):
            self.outer.write(f':sense{cnum}:sweep:time:auto {int(state)}')

        def get_time_auto(self, cnum):
            self.outer.query(f':sense{cnum}:sweep:time:auto?')

        def set_time(self, cnum, time: int):
            self.outer.write(f':sense{cnum}:sweep:time {time}')

        def get_time(self, cnum):
            return self.outer.query(f':sense{cnum}:sweep:time?')

    class Power:
        def __init__(self, outer):
            self.outer = outer

        def set_rf_excitation(self, state):
            self.outer.write(f':output:state {int(state)}')

        def get_rf_excitation(self):
            return self.outer.query(':output:state?')

        def set_channel_power(self, cnum, power: float):
            self.outer.write(f':source{cnum}:power {power:.2f}')

        def get_channel_power(self, cnum):
            return self.outer.query(f':source{cnum}:power?')

        def set_power_sweep_start(self, cnum, power: float):
            self.outer.write(f':source{cnum}:power:start {power:.2f}')

        def get_power_sweep_start(self, cnum):
            return self.outer.query(f':source{cnum}:power:start?')

        def set_power_sweep_stop(self, cnum, power: float):
            self.outer.write(f':source{cnum}:power:stop {power:.2f}')

        def get_power_sweep_stop(self, cnum):
            return self.outer.query(f':source{cnum}:power:stop?')

    class Frequency:
        def __init__(self, outer):
            self.outer = outer

        def get_start(self, cnum):
            return self.outer.query(f':sense{cnum}:frequency:start?')

        def set_start(self, cnum, frequency: float):
            self.outer.write(f':sense{cnum}:frequency:start {frequency}')

        def get_stop(self, cnum):
            return self.outer.query(f':sense{cnum}:frequency:stop?')

        def set_stop(self, cnum, frequency: float):
            self.outer.write(f':sense{cnum}:frequency:stop {frequency}')

        def get_center(self, cnum):
            return self.outer.query(f':sense{cnum}:frequency:center?')

        def set_center(self, cnum, frequency: float):
            self.outer.write(f':sense{cnum}:frequency:center {frequency}')

        def get_span(self, cnum):
            return self.outer.query(f':sense{cnum}:frequency:span?')

        def set_span(self, cnum, frequency: float):
            self.outer.write(f':sense{cnum}:frequency:span {frequency}')

        def get_cw(self, cnum):
            return self.outer.query(f':sense{cnum}:frequency:cw?')

        def set_cw(self, cnum, frequency: float):
            self.outer.write(f':sense{cnum}:frequency:cw {frequency}')

    class SaveRcall:
        def __init__(self, outer):
            self.outer = outer

        def load_correction(self, filename):
            self.outer.do_command(f':mmemory:load:correction "{filename}"')

        def load_csarchive(self, filename):
            self.outer.do_command(f':mmemory:load:csarchive "{filename}"')

        def load(self, filename):
            self.outer.write(f':mmemory:load "{filename}"')

        def store_csarchive(self, filename):
            """
            保存指定的状态+校准数据文件（即*.csa文件）。
            :param filename: 表示状态+校准数据文件，其范围少于255个字符。
            :return: 无
            """
            self.outer.do_command(f':mmemory:store:csarchive "{filename}"')

        def store_file(self, filename):
            """
            存储指定的系统状态文件。支持存储.sta，.csa和.cal状态文件。如果已经存在与指定文件名相同的文件，则会重写其内容。
            :param filename: 表示系统状态文件，其范围少于255个字符。
            :return:
            """
            self.outer.do_command(f':mmemory:store "{filename}"')

        def store_image(self, filename):
            """
            将LCD屏幕上的显示图像保存到位图格式（扩展名为".bmp"）或便携网络图形格式（扩展名为".png"）或JPEG文件交换格式（扩展名为".jpg"）的文件中。
            :param filename: 表示图像格式文件，其范围255个字符或更少。
            :return:
            """
            self.outer.do_command(f':mmemory:store:image "{filename}"')

        def store_correction(self, filename):
            """
            保存校准数据到文件。
            :param filename: 表示校准文件，其范围少于255个字符。
            :return:
            """
            self.outer.do_command(f':mmemory:store:correction "{filename}"')

        def store_format_data(self, filename):
            """
            存储活动迹线的格式化数据阵列。如果已经存在与指定文件名相同的文件，则会重写其内容。
            :param filename: 表示格式化数据文件(*.CSV)。
            :return:
            """
            self.outer.do_command(f':mmemory:store:fdata "{filename}"')

        def transfer_read(self, filename) -> str:
            """
            将数据写入文件或从文件读取数据。
            :param filename: 表示文件名。
            :return:
            """
            return self.outer.query(f':mmemory:transfer? "{filename}"')

        def transfer_write(self, filename, block):
            raise NotImplementedError("This function is not implemented in the original code.")

        def set_snp_format(self, _type: str = 'auto'):
            raise NotImplementedError("This function is not implemented in the original code.")

        def get_snp_format(self):
            raise NotImplementedError("This function is not implemented in the original code.")

        def store_snp(self, filename):
            """
            将工作通道的测量数据保存到标准格式的文件。在保存文件之前，您需要指定文件格式和文件类型。文件类型不同扩展名也不同，如下所示：
            .s1p:指定1个端口
            .s2p:指定2个端口
            .s3p:指定3个端口
            .s4p:指定4个端口
            :param filename: 表示SNP文件，其范围255个字符或更少。
            :return:
            """
            self.outer.write(f':mmemory:store:snp "{filename}"')

    class Marker:
        def __init__(self, outer):
            self.outer = outer

        def close_all(self, cnum, tnum):
            self.outer.write(f':calculate{cnum}:measure{tnum}:marker:aoff')

        def set_state(self, cnum, tnum, mnum, state: bool):
            self.outer.write(f':calculate{cnum}:measure{tnum}:marker{mnum}:state {int(state)}')

        def get_state(self, cnum, tnum, mnum):
            return self.outer.query(f':calculate{cnum}:measure{tnum}:marker{mnum}:state?')

        def set_x_value(self, cnum, tnum, mnum, value):
            self.outer.write(f':calculate{cnum}:trace{tnum}:marker{mnum}:x {str(value)}')

        def get_x_value(self, cnum=1, tnum=1, mnum=1):
            return self.outer.query_ascii_values(f':calculate{cnum}:trace{tnum}:marker{mnum}:x?')

        def get_y_value(self, cnum=1, tnum=1, mnum=1):
            r, i = self.outer.query_ascii_values(f':calculate{cnum}:trace{tnum}:marker{mnum}:y?')
            return (r, i)

    class Format:
        def __init__(self, outer):
            self.outer = outer
            self.transmission_format = 'ascii'

        def set_trace_format(self, cnum=1, tnum=1, _type: str = 'scomplex'):
            assert _type.lower() in TraceDataFormat
            self.outer.write(f':calculate{cnum}:trace{tnum}:format {_type}')

        def get_trace_format(self, cnum=1, tnum=1):
            return self.outer.query(f':calculate{cnum}:trace{tnum}:format?')

        def set_transmission_format(self, _type: str = 'ascii'):
            assert _type.lower() in {"ascii", "real", "real32"}
            self.transmission_format = _type
            self.outer.write(f':format:data {_type}')

        def get_transmission_format(self):
            return self.outer.query(':format:data?')

        def get_channel_frequency_array(self, cnum=1):
            if self.transmission_format == 'ascii':
                return self.outer.query_ascii_values(f':sense{cnum}:frequency:data?')
            else:
                return self.outer.query_binary_values(f':sense{cnum}:frequency:data?')

        def get_format_data_array(self, cnum=1, tnum=1):
            if self.transmission_format == 'ascii':
                return self.outer.query_ascii_values(f':calculate{cnum}:trace{tnum}:data:fdata?')
            else:
                return self.outer.query_binary_values(f':calculate{cnum}:trace{tnum}:data:fdata?')

        # set

        def get_multiple_trace_data(self, cnum=1, tnums=[1]):
            query = f':calculate{cnum}:data:MFData? "{",".join(map(str, tnums))}"'
            print(query)
            if self.transmission_format == 'ascii':
                return self.outer.query_ascii_values(query)
            else:
                return self.outer.query_binary_values(query)

    class Scale:
        def __init__(self, outer):
            self.outer = outer

        def set_trace_scale_auto(self, wnum, tnum):
            self.outer.write(f':display:window{wnum}:trace{tnum}:y:scale:auto')

        def set_all_trace_scale_auto(self, wnum):
            self.outer.write(f':display:window{wnum}:y:auto')

        def set_scale_division(self, wnum, tnum, division):
            """
            Set the scale division of the trace
            :param wnum:
            :param tnum:
            :param division:
            :return:
            """
            self.outer.write(f':display:window{wnum}:trace{tnum}:y:pdivision {division}')

        def get_scale_division(self, wnum, tnum):
            return self.outer.query(f':display:window{wnum}:trace{tnum}:y:pdivision?')

        def set_scale_reference_level(self, wnum, tnum, level):
            self.outer.write(f':display:window{wnum}:trace{tnum}:y:rlevel {level}')

        def get_scale_reference_level(self, wnum, tnum):
            return self.outer.query(f':display:window{wnum}:trace{tnum}:y:rlevel?')

    class Measure:
        def __init__(self, outer):
            self.outer = outer

        InstrumentType = {'VNA', 'SA', 'SMM'}

        def set_instrument_type(self, cnum, instrument_type: str):
            assert instrument_type.upper() in self.InstrumentType
            self.outer.write(f':calculate{cnum}:instrument {instrument_type}')

        def get_instrument_type(self, cnum):
            return self.outer.query(f':calculate{cnum}:instrument?')

        def set_parameter(self, cnum, tnum, parameter):
            self.outer.write(f':calculate{cnum}:parameter{tnum}:define {parameter}')

        def get_parameter(self, cnum, tnum):
            return self.outer.query(f':calculate{cnum}:parameter{tnum}:define?')
