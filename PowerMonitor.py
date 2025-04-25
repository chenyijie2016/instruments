import serial


class PowerMonitor(object):
    def __init__(self, serial_address):
        self.serial = serial.Serial(serial_address, 115200, )

    def configure(self, freq, sps, trigger, trigger_level=-30):
        """

        :param freq: RF Frequency in MHz
        :param sps: Sampling rate in SPS: 500k,200k,100k,50k,20k,10k,5k,2k,1k for 0-8
        :param trigger: Trigger Type 0: auto, 1: raising, 2: falling
        :param trigger_level: Trigger Level in dBm (-30 to +25) ，最高位为1时代表功率为负数，例如 +25dBm 表示为 0 x19 25 表示为 0 x99
        :return:
        """
        command_frame_header = bytearray([0x10, 0x08, 0x01])
        command_freq = bytearray([freq >> 8, freq & 0xFF])  # high byte first,
        command_sample = bytearray([sps])
        command_trigger = bytearray([trigger])
        # 将dbm转换为十六进制
        if trigger_level < 0:
            trigger_level = 0x80 | (trigger_level & 0x7F)
        else:
            trigger_level = 0x00 | (trigger_level & 0x7F)
        command_trigger_level = bytearray([trigger_level, 0x00])
        command_reserved = bytearray([0x00])
        # 校验位 02- 09 求和取低八位
        checksum = (
                sum([0x01]) +
                sum(command_freq) +
                sum(command_sample) +
                sum(command_trigger) +
                sum(command_trigger_level) +
                sum(command_reserved)
        ) & 0xFF

        command_checksum = bytearray([0x00])


