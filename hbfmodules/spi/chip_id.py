import serial
import codecs

from hydrabus_framework.modules.AModule import AModule
from hydrabus_framework.utils.hb_generic_cmd import hb_connect_bbio, hb_reset, hb_close
from hydrabus_framework.utils.protocols.spi import hb_switch_spi, hb_configure_spi_port


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
        self.serial = serial.Serial()
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

    def connect(self):
        """
        Connect to hydrabus and switch into BBIO mode
        :return: Bool
        """
        try:
            device = self.get_option_value("hydrabus")
            self.serial = hb_connect_bbio(device=device, baudrate=115200, timeout=1)
            if not self.serial:
                raise UserWarning("Unable to connect to hydrabus device")
            return True
        except UserWarning as err:
            self.logger.handle("{}".format(err), self.logger.ERROR)
            return False

    def init_hydrabus(self):
        """
        Manage connection and init of the hydrabus into BBIO spi mode
        :return: Bool
        """
        if self.connect():
            if hb_switch_spi(self.serial):
                return True
            else:
                self.logger.handle("Unable to switch hydrabus in spi mode, please reset it", self.logger.ERROR)
                return False
        else:
            self.logger.handle("Unable to connect to hydrabus", self.logger.ERROR)
            return False

    def chip_id(self):
        buf = bytearray()
        self.logger.handle("Sending RDID command...", self.logger.INFO)
        # write-then-read: write one byte, read 3 (rdid)
        self.serial.write(b'\x04\x00\x01\x00\x03')

        # send rdid byte (0x9f)
        self.serial.write(b'\x9f')

        hb_ret = self.serial.read(1)
        if b'\x01' == hb_ret:
            buf = self.serial.read(3)
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
            result = hb_configure_spi_port(self.serial,
                                           polarity=self.get_option_value("spi_polarity"),
                                           phase=self.get_option_value("spi_phase"),
                                           spi_device=self.get_option_value("spi_device"))
            if result:
                self.chip_id()
            self.logger.handle("Reset hydrabus to console mode", self.logger.INFO)
            hb_reset(self.serial)
            hb_close(self.serial)
