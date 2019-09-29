import serial
import codecs

from hydrabus_framework.modules.AModule import AModule
from hydrabus_framework.utils.pyHydrabus.spi import SPI


__author__ = "Jordan Ovrè <ghecko78@gmail.com>"


class ClassName(AModule):
    def __init__(self, hbf_config):
        super(ClassName, self).__init__(hbf_config)
        self.meta.update({
            'name': 'SPI chip ID',
            'version': '0.0.1',
            'description': 'Module to recover SPI chip ID',
            'author': 'Jordan Ovrè <ghecko78@gmail.com>'
        })
        self.hb_serial = None
        self.options = [
            {"Name": "hydrabus", "Value": "", "Required": True, "Type": "string",
             "Description": "Hydrabus device", "Default": self.config["HYDRABUS"]["port"]},
            {"Name": "timeout", "Value": "", "Required": True, "Type": "int",
             "Description": "Hydrabus read timeout", "Default": self.config["HYDRABUS"]["read_timeout"]},
            {"Name": "spi_device", "Value": "", "Required": True, "Type": "string",
             "Description": "The hydrabus SPI device (SPI1 or SPI2)", "Default": "SPI1"},
            {"Name": "spi_polarity", "Value": "", "Required": True, "Type": "string",
             "Description": "set SPI polarity (high or low)", "Default": "low"},
            {"Name": "spi_phase", "Value": "", "Required": True, "Type": "string",
             "Description": "set SPI phase (high or low)", "Default": "low"}
        ]

    def init_hydrabus(self):
        """
        Manage connection and init of the hydrabus into BBIO spi mode
        :return: Bool
        """
        try:
            device = self.get_option_value("hydrabus")
            timeout = int(self.get_option_value("timeout"))
            self.hb_serial = SPI(device)
            self.hb_serial.timeout = timeout
            self.hb_serial.polarity = self.get_option_value("spi_polarity")
            self.hb_serial.phase = self.get_option_value("spi_phase")
            self.hb_serial.device = self.get_option_value("spi_device")
            return True
        except serial.SerialException as err:
            self.logger.handle("{}".format(err), self.logger.ERROR)
            return False

    def chip_id(self):
        self.logger.handle("Sending RDID command...", self.logger.INFO)
        # write-then-read: write one byte, read 3 (rdid); \x9f = rdid command
        buf = self.hb_serial.write_read(data=b'\x9f', read_len=3)
        if buf is not None:
            cid = codecs.encode(buf, 'hex').decode().upper()
            manufacturer = cid[0:2]
            mem_type = cid[2:4]
            dev_id = cid[4:6]
            self.logger.handle(f"Chip ID: {manufacturer} {mem_type} {dev_id}", self.logger.RESULT)
        else:
            self.logger.handle("Unable to send RDID SPI command to hydrabus...", self.logger.ERROR)

    def run(self):
        """
        Main function.
        The aim of this module is to recover SPI Chip ID
        :return: Nothing
        """
        if self.init_hydrabus():
            self.chip_id()
            self.logger.handle("Reset hydrabus to console mode", self.logger.INFO)
            self.hb_serial.close()
