# -*- coding: utf-8 -*-

import pytest
import mock
from mix.driver.smartgiant.common.ipcore.mix_ads8568_sg import MIXADS8568SG
from mix.driver.smartgiant.common.ipcore.mix_ads8568_sg import MIXADS8568SGDef

__author__ = 'jionghao.huang@SmartGiant'
__version__ = '0.1'


@pytest.fixture(scope='module')
def mix_ads8568_sg():
    axi4_bus = mock.Mock()
    convst_a = mock.Mock()
    convst_b = mock.Mock()
    convst_c = mock.Mock()
    convst_d = mock.Mock()
    busy = mock.Mock()
    xclk = mock.Mock()
    hw_sw_sel = mock.Mock()
    ref_sel = mock.Mock()
    stby = mock.Mock()
    reset = mock.Mock()
    cs = mock.Mock()
    refbuf_en = mock.Mock()
    asleep_sel = mock.Mock()
    ser_sel = mock.Mock()
    sel_cd = mock.Mock()
    sel_b = mock.Mock()
    mix_ads8568_sg = MIXADS8568SG(axi4_bus, convst_a, convst_b, convst_c, convst_d,
                                  busy, xclk, hw_sw_sel, ref_sel, stby, reset, cs, refbuf_en, asleep_sel,
                                  ser_sel, sel_cd, sel_b)
    return mix_ads8568_sg


@pytest.fixture(params=['enable', 'disable'])
def status(request):
    return request.param


@pytest.fixture(params=['A', 'B', 'C', 'D'])
def ch_pair(request):
    return request.param


@pytest.fixture(params=['sw', 'hw'])
def dev_func_mode(request):
    return request.param


@pytest.fixture(params=[1, 2, 3, 4])
def count(request):
    return request.param


@pytest.fixture(params=['4VREF', '2VREF'])
def vrange(request):
    return request.param


@pytest.fixture(params=[2.5, 3])
def max_vref_range(request):
    return request.param


@pytest.fixture(params=[1, 2, 3, 4, 5, 6, 7, 8])
def ch(request):
    return request.param


def test_ctrl_dev(mix_ads8568_sg, status):
    with mock.patch.object(mix_ads8568_sg.axi4_bus, 'write_8bit_inc') as mock_write_8bit_inc:
        mix_ads8568_sg.ctrl_dev(status)
    # mock_write.assert_called_with(dev_addr, [register, last_data])


def test_write_config_register(mix_ads8568_sg):
    wr_data = 0xC00003FF
    with mock.patch.object(mix_ads8568_sg.axi4_bus, 'write_32bit_inc') as mock_write_32bit_inc:
        mix_ads8568_sg.write_config_register(wr_data)


def test_read_config_register(mix_ads8568_sg):
    with mock.patch.object(mix_ads8568_sg.axi4_bus, 'read_32bit_inc') as mock_read_32bit_inc:
        mix_ads8568_sg.read_config_register()


def test_sel_b_ch(mix_ads8568_sg, status):
    with mock.patch.object(mix_ads8568_sg.axi4_bus, 'write_8bit_inc') as mock_write_8bit_inc:
        mix_ads8568_sg.sel_b_ch(status)


def test_sel_cd_ch(mix_ads8568_sg, status):
    with mock.patch.object(mix_ads8568_sg.axi4_bus, 'write_8bit_inc') as mock_write_8bit_inc:
        mix_ads8568_sg.sel_cd_ch(status)


def test_set_spi_speed(mix_ads8568_sg):
    speed = 10000000
    with mock.patch.object(mix_ads8568_sg.axi4_bus, 'write_32bit_inc') as mock_write_32bit_inc:
        mix_ads8568_sg.set_spi_speed(speed)


def test_adc_ch_pair_en(mix_ads8568_sg, count):
    with mock.patch.object(mix_ads8568_sg.axi4_bus, 'write_8bit_inc') as mock_write_8bit_inc:
        mix_ads8568_sg.adc_ch_pair_en(count)


def test_read_single_ch_data(mix_ads8568_sg, ch_pair):
    with mock.patch.object(mix_ads8568_sg.axi4_bus, 'read_32bit_inc') as mock_read_32bit_inc:
        mix_ads8568_sg.read_single_ch_data(ch_pair)


def test_read_all_ch_data(mix_ads8568_sg):
    with mock.patch.object(mix_ads8568_sg.axi4_bus, 'read_32bit_inc') as mock_read_32bit_inc:
        mix_ads8568_sg.read_all_ch_data()


def test_sel_mode(mix_ads8568_sg, dev_func_mode):
    mix_ads8568_sg.sel_mode(dev_func_mode)


def test_sel_mode(mix_ads8568_sg):
    mix_ads8568_sg.init_pins()


def test_reset_dev(mix_ads8568_sg):
    mix_ads8568_sg.reset_dev()


def test_init_dev(mix_ads8568_sg, dev_func_mode):
    mix_ads8568_sg.init_dev(dev_func_mode)


def test_set_absolute_volt_range(mix_ads8568_sg, dev_func_mode, vrange, ch_pair):
    with mock.patch.object(mix_ads8568_sg, 'read_config_register') as mock_read_config_register:
        with mock.patch.object(mix_ads8568_sg, 'write_config_register') as mock_write_config_register:
            mix_ads8568_sg.set_absolute_volt_range(dev_func_mode, vrange, ch_pair)


def test_sel_max_vref_output_range(mix_ads8568_sg, max_vref_range):
    with mock.patch.object(mix_ads8568_sg, 'read_config_register') as mock_read_config_register:
        with mock.patch.object(mix_ads8568_sg, 'write_config_register') as mock_write_config_register:
            mix_ads8568_sg.sel_max_vref_output_range(max_vref_range)


def test_set_inter_vref(mix_ads8568_sg, dev_func_mode):
    internal_ref_volt = 3.0
    with mock.patch.object(mix_ads8568_sg, 'read_config_register') as mock_read_config_register:
        with mock.patch.object(mix_ads8568_sg, 'write_config_register') as mock_write_config_register:
            mix_ads8568_sg.set_inter_vref(dev_func_mode, internal_ref_volt)


def test_start_conv(mix_ads8568_sg, ch_pair):
    mix_ads8568_sg.start_conv(ch_pair)


def test__code_2_mvolt(mix_ads8568_sg):
    code = 0x1234FF78
    mix_ads8568_sg._code_2_mvolt(code)


def test_read_ch(mix_ads8568_sg, ch):
    with mock.patch.object(mix_ads8568_sg.busy, 'get_level', return_value=0) as mock_get_level:
        with mock.patch.object(mix_ads8568_sg, 'read_single_ch_data',
                               return_value=0x1234FF78) as mock_read_single_ch_data:
            mix_ads8568_sg.read_ch(ch)


def test_scan_ch(mix_ads8568_sg):
    ch_list = [1, 2, 3, 4, 5, 6, 7, 8]
    with mock.patch.object(mix_ads8568_sg.busy, 'get_level', return_value=0) as mock_get_level:
        with mock.patch.object(mix_ads8568_sg, 'read_single_ch_data',
                               return_value=0x1234FF78) as mock_read_single_ch_data:
            mix_ads8568_sg.scan_ch(ch_list)
