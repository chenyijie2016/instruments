import logging
import sys

import pyvisa


class VISAInstrument(object):

    def __init__(self, visa_address, instrument_name=''):
        self.visa_address = visa_address
        rm = pyvisa.ResourceManager()
        rm.timeout = 5000
        self.resource = rm.open_resource(visa_address)
        self.logger = logging.getLogger(instrument_name)

    def do_command(self, command):
        self.logger.info("do_command-->[%s]", command)
        self.resource.write(command)
        self.check_instrument_error(command)

    def do_command_ieee_block(self, command, values):
        self.logger.info("do_command_ieee_block-->[%s]", command)
        self.resource.write_binary_values(f"{command} ", values, datatype='B')
        self.check_instrument_error(command)


    def do_query_string(self, query):
        self.logger.info("do_query_string-->[%s]", query)
        result = self.resource.query(query)
        self.logger.info("result<--[%s]", result)
        self.check_instrument_error(query)
        return result

    def do_query_number(self, query):
        self.logger.info("do_query_number-->[%s]", query)
        result = self.resource.query(query).strip()
        self.logger.info("result<--[%s]", result)
        self.check_instrument_error(query)
        return float(result)

    def do_query_ieee_block(self, query):
        self.logger.info("do_query_ieee_block-->[%s]", query)
        result = self.resource.query_binary_values(f"{query}", datatype='s', container=bytes)
        self.logger.info("result<--[%s]", result)
        self.check_instrument_error(query)
        return result

    def query(self, command):
        self.logger.info("query-->[%s]", command)
        response = self.resource.query(command).strip()
        self.logger.info("response<--[%s]", response.strip())
        return response

    def write(self, command) -> None:
        self.logger.info("query-->[%s]", command)
        self.resource.write(command)

    def query_ascii_values(self, command):
        self.logger.info("query-->[%s]", command)
        response = self.resource.query_ascii_values(command, converter='f', separator=',')
        self.logger.info("response<--[%s]", response)
        return response

    def query_binary_values(self, command):
        self.logger.info("query-->[%s]", command)
        response = self.resource.query_binary_values(command, datatype='f', is_big_endian=False)
        self.logger.info("response<--[%s]", response)
        return response

    def check_instrument_error(self, command=''):
        # self.logger.info("check_instrument_error")
        while True:
            error_string = self.resource.query(':system:error?')
            if error_string:
                if error_string.find("+0,", 0, 3) == -1:
                    self.logger.error("ERROR: [%s] Cmd: [%s]", error_string, command)
                    sys.exit(1)
                else:
                    break
            else:
                logging.error("ERROR :system:error? returned nothing, command: %s", command)
