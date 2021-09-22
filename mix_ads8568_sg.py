# -*- coding: utf-8 -*-
import time
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus

__author__ = 'jionghao.huang@SmartGiant'
__version__ = '0.1'


class MIXADS8568SGDef:
    MODULE_STATUS = 0x10  # 1bit
    ADS8568_SEL_B = 0x11  # 1bit
    ADS8568_SEL_CD = 0x12  # 1bit
    ADC_SPI_RATE = 0x14  # 32bit
    SPI_NORMAL_DATA = 0x18  # 32bit
    DATA_LEN = 4
    ADC_CHANNEL_EN = 0x20  # 4bit
    CHANNEL_A_DATA = 0x24  # 32bit
    CHANNEL_B_DATA = 0x28  # 32bit
    CHANNEL_C_DATA = 0x2C  # 32bit
    CHANNEL_D_DATA = 0x30  # 32bit

    STATUS = {'enable': 0x01, 'disable': 0x00}
    CHANNEL_PAIR = {'A': CHANNEL_A_DATA, 'B': CHANNEL_B_DATA, 'C': CHANNEL_C_DATA, 'D': CHANNEL_D_DATA}

    # Config register mask.
    INTERNAL_VREF_EN = 0x00001000
    INTERNAL_VREF_DIS = 0x00000000
    WR_RD_CONFIG_REG = 0xC0000000
    # Hardware mode related register.
    # Bit 30
    READ_EN_NORMAL = 0x00000000
    READ_EN_TWO_ACCESSES = 0x40000000
    # Bit 29
    CLKSEL_NORMAL = 0x00000000
    CLKSEL_EXTERNAL = 0x20000000
    # Bit 27
    BUSY_MODE = 0x00000000
    INTERRUPT_MODE = 0x08000000
    # Bit 26
    ACTIVE_HIGH = 0x00000000
    ACTIVE_LOW = 0x04000000
    # Bit 22
    PD_B_NORMAL = 0x00000000
    PD_B_POWER_DOWN = 0x00400000
    # Bit 20
    PD_C_NORMAL = 0x00000000
    PD_C_POWER_DOWN = 0x00100000
    # Bit 18
    PD_D_NORMAL = 0x00000000
    PD_D_POWER_DOWN = 0x00040000
    # Bit 13
    VREF_2500_MV = 0x00000000
    VREF_3000_MV = 0x00002000

    POSITIVE_FULL_SCALE = 0x7FFF

    DEV_FUNC_MODE = {'sw': 0, 'hw': 1}
    CHANNEL = {1: 'A', 2: 'A', 3: 'B', 4: 'B', 5: 'C', 6: 'C', 7: 'D', 8: 'D'}
    HW_ABSOLUTE_VOLT_RANGE = {'4VREF': 0, '2VREF': 1}
    SW_ABSOLUTE_VOLT_RANGE = {
        'A': {'4VREF': 0, '2VREF': 0x01000000},
        'B': {'4VREF': 0, '2VREF': 0x00800000},
        'C': {'4VREF': 0, '2VREF': 0x00200000},
        'D': {'4VREF': 0, '2VREF': 0x00080000}
    }
    MAX_VREF_OUTPUT_RANGE = {2.5: VREF_2500_MV, 3: VREF_3000_MV}

    CH_MIN = 1
    CH_MAX = 8


class MIXADS8568SG(object):
    '''
    MIXADS8568SG is the ipcore of chip ads8568.

    '''

    def __init__(self, axi4_bus, convst_a=None, convst_b=None, convst_c=None, convst_d=None,
                 busy=None, xclk=None, hw_sw_sel=None, ref_sel=None, stby=None, reset=None,
                 cs=None, refbuf_en=None, asleep_sel=None, ser_sel=None, sel_cd=None, sel_b=None):
        self.axi4_bus = axi4_bus
        self.convst_a = convst_a
        self.convst_b = convst_b
        self.convst_c = convst_c
        self.convst_d = convst_d
        self.busy = busy
        self.xclk = xclk
        self.hw_sw_sel = hw_sw_sel
        self.ref_sel = ref_sel
        self.stby = stby
        self.reset = reset
        self.cs = cs
        self.refbuf_en = refbuf_en
        self.asleep_sel = asleep_sel
        self.ser_sel = ser_sel
        self.sel_cd = sel_cd
        self.sel_b = sel_b

        self.dev_func_mode = 'hw'
        self.max_vref_range = 2.5
        self.input_volt_range = 4 * self.max_vref_range
        self.current_config_data = 0x000003FF

    def ctrl_dev(self, status):
        '''
        MIXADS8568SG control device.

        Args:
            status:  string, ['enable', 'disable'], device status.

        Examples:
            mixads8568sg.ctrl_dev('enable')

        '''
        assert status in MIXADS8568SGDef.STATUS

        self.axi4_bus.write_8bit_inc(MIXADS8568SGDef.MODULE_STATUS, [MIXADS8568SGDef.STATUS[status]])

    def write_config_register(self, wr_data):
        '''
        MIXADS8568SG wirte config register.(0nly effective in sw mode.)

        Args:
            wr_data:  int, [0x0 ~ 0xFFFFFFFF], data to write.

        Examples:
            mixads8568sg.write_config_register(0xC00003FF)

        '''
        assert isinstance(wr_data, int)
        assert 0x00000000 <= wr_data <= 0xFFFFFFFF

        self.axi4_bus.write_32bit_inc(MIXADS8568SGDef.SPI_NORMAL_DATA, [wr_data])

    def read_config_register(self):
        '''
        MIXADS8568SG read config register.(0nly effective in sw mode.)

        Examples:
            mixads8568sg.read_config_register()

        '''
        # Need debug.
        wr_data = MIXADS8568SGDef.WR_RD_CONFIG_REG | self.current_config_data
        self.write_config_register(wr_data)
        self.start_conv('A')
        # time.sleep(0.001)
        rd_data = self.axi4_bus.read_32bit_inc(MIXADS8568SGDef.SPI_NORMAL_DATA, MIXADS8568SGDef.DATA_LEN)

        return rd_data[0]

    def sel_b_ch(self, status):
        '''
        MIXADS8568SG select channel pair B.

        Args:
            status:  string, ['enable', 'disable'], channel status.

        Examples:
            mixads8568sg.sel_b_ch('enable')

        '''
        assert status in MIXADS8568SGDef.STATUS

        self.axi4_bus.write_8bit_inc(MIXADS8568SGDef.ADS8568_SEL_B, [MIXADS8568SGDef.STATUS[status]])

    def sel_cd_ch(self, status):
        '''
        MIXADS8568SG select channel pair C and D.

        Args:
            status:  string, ['enable', 'disable'], channel status.

        Examples:
            mixads8568sg.sel_cd_ch('enable')

        '''
        assert status in MIXADS8568SGDef.STATUS

        self.axi4_bus.write_8bit_inc(MIXADS8568SGDef.ADS8568_SEL_CD, [MIXADS8568SGDef.STATUS[status]])

    def set_spi_speed(self, speed):
        '''
        MIXADS8568SG set spi bus clock speed.

        Args:
            speed:  int, [1 ~ 20000000], unit Hz, 1000000 means 1000000Hz.

        Examples:
            mixads8568sg.set_spi_speed(10000000)

        '''
        assert 1 <= speed <= 20000000

        wr_data = (pow(2, 32) * 8 * speed) / 1000000000
        self.axi4_bus.write_32bit_inc(MIXADS8568SGDef.ADS8568_SEL_CD, [wr_data])

    def adc_ch_pair_en(self, count):
        '''
        MIXADS8568SG set spi bus clock speed.

        Args:
            count:  int, [1 ~ 4], unit Hz, 1000000 means 1000000Hz.

        Examples:
            mixads8568sg.adc_ch_pair_en(4)

        '''
        assert 1 <= count <= 4

        self.axi4_bus.write_8bit_inc(MIXADS8568SGDef.ADC_CHANNEL_EN, [count])

    def read_single_ch_data(self, ch_pair):
        '''
        MIXADS8568SG set spi bus clock speed.

        Args:
            ch_pair:  int, ['A', 'B', 'C', 'D'], channel pair.

        Returns:
            rd_data,  int.

        Examples:
            mixads8568sg.read_single_ch_data('A')

        '''
        assert ch_pair in MIXADS8568SGDef.CHANNEL_PAIR

        rd_data = self.axi4_bus.read_32bit_inc(MIXADS8568SGDef.CHANNEL_PAIR[ch_pair], MIXADS8568SGDef.DATA_LEN)
        return rd_data[0]

    def read_all_ch_data(self):
        '''
        MIXADS8568SG read all channels data.

        Returns:
            rd_data,  list.

        Examples:
            mixads8568sg.read_all_ch_data()

        '''
        ch_a_data = self.axi4_bus.read_32bit_inc(MIXADS8568SGDef.CHANNEL_A_DATA, MIXADS8568SGDef.DATA_LEN)
        ch_b_data = self.axi4_bus.read_32bit_inc(MIXADS8568SGDef.CHANNEL_B_DATA, MIXADS8568SGDef.DATA_LEN)
        ch_c_data = self.axi4_bus.read_32bit_inc(MIXADS8568SGDef.CHANNEL_C_DATA, MIXADS8568SGDef.DATA_LEN)
        ch_d_data = self.axi4_bus.read_32bit_inc(MIXADS8568SGDef.CHANNEL_D_DATA, MIXADS8568SGDef.DATA_LEN)
        return ch_a_data[0] + ch_b_data[0] + ch_c_data[0] + ch_d_data[0]

    def sel_mode(self, dev_func_mode='hw'):
        '''
        MIXADS8568SG select device functional mode.

        Args:
            dev_func_mode:    string, ['sw', 'hw'], device functional mode.

        Examples:
            mixads8568sg.sel_mode('hw')

        '''
        assert dev_func_mode in MIXADS8568SGDef.DEV_FUNC_MODE

        self.hw_sw_sel.set_level(MIXADS8568SGDef.DEV_FUNC_MODE[dev_func_mode])

    def init_pins(self):
        '''
        MIXADS8568SG init pins.

        Examples:
            mixads8568sg.init_pins()

        '''
        self.convst_a.set_dir('output')
        self.convst_b.set_dir('output')
        self.convst_c.set_dir('output')
        self.convst_d.set_dir('output')
        self.xclk.set_dir('output')
        self.hw_sw_sel.set_dir('output')
        self.ref_sel.set_dir('output')
        self.stby.set_dir('output')
        self.reset.set_dir('output')
        self.cs.set_dir('output')
        self.refbuf_en.set_dir('output')
        self.asleep_sel.set_dir('output')
        self.ser_sel.set_dir('output')
        self.sel_cd.set_dir('output')
        self.sel_b.set_dir('output')
        self.busy.set_dir('input')

    def reset_dev(self):
        '''
        MIXADS8568SG reset, active high. This pin aborts any ongoing conversions and resets the internal
        configuration register(CONFIG) to 000003FFh.A valid reset pulse must be at least 50 ns long.

        Examples:
            mixads8568sg.reset_dev()

        '''
        self.reset.set_level(0)
        time.sleep(0.001)
        self.reset.set_level(1)
        time.sleep(0.001)
        self.reset.set_level(0)

    def init_dev(self, dev_func_mode):
        '''
        MIXADS8568SG init device.

        Args:
            dev_func_mode:    string, ['sw', 'hw'], device functional mode.

        Examples:
            mixads8568sg.init_dev()

        '''
        assert dev_func_mode in MIXADS8568SGDef.DEV_FUNC_MODE

        self.sel_mode(dev_func_mode)
        self.init_pins()
        self.reset_dev()
        # Enable FPGA IP.
        self.ctrl_dev('enable')

    def sel_max_vref_output_range(self, max_vref_range=2.5):
        '''
        MIXADS8568SG set maximum reference voltage output range.

        Args:
            max_vref_range:    int, [2.5, 3]V, maximum reference voltage output range.

        Examples:
            mixads8568sg.sel_max_vref_output_range(3)

        '''
        assert max_vref_range in MIXADS8568SGDef.MAX_VREF_OUTPUT_RANGE

        range_mask = MIXADS8568SGDef.MAX_VREF_OUTPUT_RANGE[max_vref_range]
        rd_data = self.read_config_register()
        wr_data = rd_data | range_mask
        self.write_config_register(wr_data)
        self.max_vref_range = max_vref_range

    def set_absolute_volt_range(self, dev_func_mode, vrange, ch_pair='A'):
        '''
        MIXADS8568SG set absolute volt range.

        Args:
            dev_func_mode: string, ['sw', 'hw'], device function mode.
            vrange:        string, ['4VREF', '2VREF'], volt range.
            ch_pair:       string, ['A', 'B', 'C', 'D'], channel pair.

        Examples:
            mixads8568sg.set_absolute_volt_range('hw', '2VREF')

        '''
        assert dev_func_mode in MIXADS8568SGDef.DEV_FUNC_MODE
        assert vrange in MIXADS8568SGDef.HW_ABSOLUTE_VOLT_RANGE
        assert ch_pair in MIXADS8568SGDef.SW_ABSOLUTE_VOLT_RANGE

        self.input_volt_range = 4 * self.max_vref_range if '4VREF' == vrange else 2 * self.max_vref_range
        if 'hw' == dev_func_mode:
            self.xclk.set_level(MIXADS8568SGDef.HW_ABSOLUTE_VOLT_RANGE[vrange])
        else:
            rd_data = self.read_config_register()
            wr_data = rd_data | MIXADS8568SGDef.SW_ABSOLUTE_VOLT_RANGE[ch_pair][vrange]
            self.write_config_register(wr_data)

    def set_inter_vref(self, dev_func_mode, internal_ref_volt):
        '''
        MIXADS8568SG set internal reference voltage.

        Args:
            dev_func_mode:        string, ['sw', 'hw'], device function mode.
            internal_ref_volt:    float,  [0.5V~3.0] unit V, internal reference voltage.

        Examples:
            mixads8568sg.set_internal_ref_volt(3.0)

        '''
        assert dev_func_mode in MIXADS8568SGDef.DEV_FUNC_MODE
        assert 0.5 <= internal_ref_volt <= 3.0

        code = (1024 * internal_ref_volt) / self.max_vref_range - 1
        rd_data = self.read_config_register()
        wr_data = rd_data | code
        self.write_config_register(wr_data)

        if 'hw' == dev_func_mode:
            # Internal reference enable in hw mode.
            self.ref_sel.set_level(1)
        else:
            # Internal reference enable in sw mode.
            wr_data |= MIXADS8568SGDef.INTERNAL_VREF_EN
            self.write_config_register(wr_data)

    def start_conv(self, ch_pair):
        '''
        MIXADS8568SG start converting, active high.

        Args:
            ch_pair:    string, ['A', 'B', 'C', 'D'], channel pair.

        Examples:
            ads8568.start_conv('A')

        '''
        channel = {'A': self.convst_a, 'B': self.convst_b,
                   'C': self.convst_c, 'D': self.convst_d}
        assert ch_pair in channel

        channel[ch_pair].set_level(0)
        time.sleep(0.001)
        channel[ch_pair].set_level(1)
        time.sleep(0.001)
        channel[ch_pair].set_level(0)

    def _code_2_mvolt(self, code):
        '''
        MIXADS8568SG translate the code value to voltage value.

        Args:
            code:    int, code value.

        Examples:
            ads8568._code_2_mvolt(0x1234)

        '''
        # assert 0 <= code <= 0xFFFF

        # When Singular channel number.
        # if (0 <= code <= 0x7FFF):
        #     volt0 = (((code >> 16) & 0x0000FFFF) / MIXADS8568SGDef.POSITIVE_FULL_SCALE) * self.input_volt_range
        #     # When dual channel number
        #     volt1 = (code & 0x0000FFFF) * MIXADS8568SGDef.POSITIVE_FULL_SCALE * self.input_volt_range
        # elif (0x8000 <= code <= 0xFFFF):
        #     volt0 = -(((code >> 16) & 0x0000FFFF) / MIXADS8568SGDef.POSITIVE_FULL_SCALE) * self.input_volt_range
        #     # When dual channel number
        #     volt1 = -(code & 0x0000FFFF) * MIXADS8568SGDef.POSITIVE_FULL_SCALE * self.input_volt_range
        assert 0 <= code <= 0xFFFFFFFF

        code0 = (((code >> 16) & 0x0000FFFF))
        code1 = (code & 0x0000FFFF)
        if (0 <= code0 <= 0x7FFF):
            volt0 = (code0 / MIXADS8568SGDef.POSITIVE_FULL_SCALE) * self.input_volt_range
        elif (0x8000 <= code0 <= 0xFFFF):
            volt0 = -(code0 / MIXADS8568SGDef.POSITIVE_FULL_SCALE) * self.input_volt_range

        if (0 <= code1 <= 0x7FFF):
            volt1 = (code1 / MIXADS8568SGDef.POSITIVE_FULL_SCALE) * self.input_volt_range
        elif (0x8000 <= code1 <= 0xFFFF):
            volt1 = -(code1 / MIXADS8568SGDef.POSITIVE_FULL_SCALE) * self.input_volt_range

        return [volt0, volt1]

    # def ads8568_read_ch(self, ch, range, mode, polarity):

    def read_ch(self, ch):
        '''
        MIXADS8568SG read single channel.

        Args:
            ch:    int, [1~8], channel.

        Returns:
            volt,  float, volt value.

        Examples:
            ads8568.read_ch(2)
        '''
        assert ch in MIXADS8568SGDef.CHANNEL

        # Channel one-to-one correspondence.
        self.sel_cd.set_level(1)
        self.sel_cd_ch('enable')
        self.sel_b.set_level(1)
        self.sel_b_ch('enable')

        # Conversion start
        self.start_conv(MIXADS8568SGDef.CHANNEL[ch])
        time.sleep(0.001)
        while self.busy.get_level():
            pass
        self.adc_ch_pair_en(1)
        # Get volt.
        # Call spi bus read api with corresponding pin.
        code = self.read_single_ch_data(MIXADS8568SGDef.CHANNEL[ch])
        rd_data = self._code_2_mvolt(code)
        volt = rd_data[0] if (ch % 2) != 0 else rd_data[1]

        return volt

    def scan_ch(self, ch_list):
        '''
        MIXADS8568SG read multiple channel.

        Args:
            ch_list:    list, [1~8], list of channel.

        Returns:
            volt, list, volt value.

        Examples:
            ads8568.scan_ch([1, 2 ,5, 8])
        '''
        assert isinstance(ch_list, list)
        for x in range(len(ch_list)):
            assert ch_list[x] in MIXADS8568SGDef.CHANNEL

        # Channel one-to-one correspondence.
        self.sel_cd.set_level(1)
        self.sel_cd_ch('enable')
        self.sel_b.set_level(1)
        self.sel_b_ch('enable')

        tmp = []
        # A conversion start must not be issued during an ongoing conversion on the corresponding channel pair.
        # Get whole channel pair.
        for i in range(len(ch_list)):
            tmp.append(MIXADS8568SGDef.CHANNEL[ch_list[i]])
        # Remove duplicate channel pair.
        ch_pair = set(tmp)
        for ch in ch_pair:
            self.start_conv(ch)
        # self.start_conv(MIXADS8568SGDef.CHANNEL[ch])
        time.sleep(0.001)
        # Wait for conversion.
        while self.busy.get_level():
            pass
        self.adc_ch_pair_en(4)
        # Get volt.
        result_list = []
        for i in range(len(ch_list)):
            code = self.read_single_ch_data(ch_list[i])
            rd_data = self._code_2_mvolt(code)
            if 'A' == MIXADS8568SGDef.CHANNEL[ch_list[i]]:
                if 1 == ch_list[i]:
                    volt_ch1 = rd_data[0]
                    result_list.append(volt_ch1)
                elif 2 == ch_list[i]:
                    volt_ch2 = rd_data[1]
                    result_list.append(volt_ch2)
            elif 'B' == MIXADS8568SGDef.CHANNEL[ch_list[i]]:
                if 3 == ch_list[i]:
                    volt_ch3 = rd_data[0]
                    result_list.append(volt_ch3)
                elif 4 == ch_list[i]:
                    volt_ch4 = rd_data[0]
                    result_list.append(volt_ch4)
            elif 'C' == MIXADS8568SGDef.CHANNEL[ch_list[i]]:
                if 5 == ch_list[i]:
                    volt_ch5 = rd_data[0]
                    result_list.append(volt_ch5)
                elif 6 == ch_list[i]:
                    volt_ch6 = rd_data[0]
                    result_list.append(volt_ch6)
            elif 'D' == MIXADS8568SGDef.CHANNEL[ch_list[i]]:
                if 7 == ch_list[i]:
                    volt_ch7 = rd_data[0]
                    result_list.append(volt_ch7)
                elif 8 == ch_list[i]:
                    volt_ch8 = rd_data[0]
                    result_list.append(volt_ch8)

        return result_list
