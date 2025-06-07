# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

REG_RESET = 0x00
REG_INC = 0x01
REG_VALUE = 0x02
REG_CFG = 0x03

EDGE_NONE = 0
EDGE_RISING = 1
EDGE_FALLING = 2


async def write_reg(dut, reg, value):
    dut.ui_in.value = (dut.ui_in.value & 0x07) | (reg << 4) | 0x08
    dut.uio_in.value = value
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = dut.ui_in.value & 0x07


async def read_reg(dut, reg):
    dut.ui_in.value = (dut.ui_in.value & 0x03) | (reg << 4) | 0x04
    await ClockCycles(dut.clk, 1)
    result = dut.uio_out.value
    dut.ui_in.value = dut.ui_in.value & 0x03
    return result


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Test register access")

    # Set the input values you want to test
    await write_reg(dut, REG_RESET, 0)
    await write_reg(dut, REG_INC, 1)
    await write_reg(dut, REG_INC, 1)
    await write_reg(dut, REG_INC, 1)
    value = await read_reg(dut, REG_VALUE)
    assert value == 3

    dut._log.info("Test seven segment display")
    assert dut.uo_out.value == 0b01001111  # 3 encoded for seven segment display

    dut._log.info("Test rising edge detection")
    await write_reg(dut, REG_CFG, EDGE_RISING)
    await write_reg(dut, REG_RESET, 0)
    dut.ui_in.value = 0x01
    await ClockCycles(dut.clk, 20)
    value = await read_reg(dut, REG_VALUE)
    assert value == 1

    dut.ui_in.value = 0x00
    await ClockCycles(dut.clk, 10)
    assert value == 1

    dut.ui_in.value = 0x01
    await ClockCycles(dut.clk, 1)
    value = await read_reg(dut, REG_VALUE)
    assert value == 2

    dut._log.info("Test falling edge detection")
    await write_reg(dut, REG_CFG, EDGE_FALLING)
    await write_reg(dut, REG_RESET, 0)
    dut.ui_in.value = 0x00
    await ClockCycles(dut.clk, 10)
    value = await read_reg(dut, REG_VALUE)
    assert value == 1

    dut.ui_in.value = 0x01
    await ClockCycles(dut.clk, 1)
    value = await read_reg(dut, REG_VALUE)
    assert value == 1

    dut.ui_in.value = 0x00
    await ClockCycles(dut.clk, 10)
    value = await read_reg(dut, REG_VALUE)
    assert value == 2

    assert dut.uo_out.value == 0b01011011  # 2 encoded for seven segment display
