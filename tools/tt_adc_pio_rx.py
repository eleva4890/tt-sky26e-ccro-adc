# tt_adc_pio_rx.py - TT demo board (RP2040, MicroPython) SPI capture with PIO + DMA
#
# Target: 01_SPEC v3 SPI output (Mode 0, 16-bit MSB first, CS_N active low, SCLK = clk/4)
#   uio[0] = SPI_SDO  -> GPIO21
#   uio[1] = SPI_CS_N -> GPIO22
#   uio[2] = SPI_SCLK -> GPIO23   (consecutive GPIOs -> relative PIO pin indexing)
#
# Two 16-bit frames are packed into one 32-bit word (earlier frame in [31:16]) so that
# 32,768 samples fit in 64 KB of RAM. Result is written to /adc_raw.bin; fetch it with
#   mpremote cp :adc_raw.bin .
# and analyze on the PC with tools/analyze_sndr.py.
#
# Requirements: MicroPython >= 1.22 (rp2.DMA). NOT yet verified on hardware.
# setup_tt() uses the Tiny Tapeout MicroPython SDK; API names differ between SDK
# releases - adjust that function to the SDK on your board.

import time

import rp2
from machine import Pin

PIN_SDO = 21    # uio[0]
PIN_CSN = 22    # uio[1]
PIN_SCLK = 23   # uio[2]

N_SAMPLES = 32768
N_WORDS = N_SAMPLES // 2

SM_ID = 4                     # PIO1 SM0 (PIO0 may be used by the SDK for clocking)
PIO1_RXF0 = 0x50300020        # PIO1 base 0x50300000 + RXF0 offset 0x20
DREQ_PIO1_RX0 = 12


@rp2.asm_pio(in_shiftdir=rp2.PIO.SHIFT_LEFT, autopush=True, push_thresh=32,
             fifo_join=rp2.PIO.JOIN_RX)
def spi_rx16():
    wait(1, pin, 1)           # CS_N = 1 (idle): re-synchronise every frame
    wait(0, pin, 1)           # CS_N falling edge = frame start
    set(x, 15)
    label("bit")
    wait(0, pin, 2)           # SCLK low
    wait(1, pin, 2)           # SCLK rising edge (sample edge; SDO stable for 2 clk)
    in_(pins, 1)              # shift in SDO
    jmp(x_dec, "bit")


def pick_sys_freq(fs):
    """System clock that is an integer multiple of fs (avoids fractional-divider spurs)."""
    for f_sys in (120_000_000, 125_000_000, 100_000_000, 128_000_000, 130_000_000):
        if f_sys % fs == 0:
            return f_sys
    raise ValueError("choose fs that divides 100/120/125/128/130 MHz")


def setup_tt(project, fs, ui_in=0x00):
    """Select the project, set ui_in and an integer-divided clock. Adjust to your SDK."""
    import machine
    from ttboard.demoboard import DemoBoard
    from ttboard.mode import RPMode

    machine.freq(pick_sys_freq(fs))
    tt = DemoBoard.get()
    tt.mode = RPMode.ASIC_RP_CONTROL
    getattr(tt.shuttle, project).enable()
    tt.uio_oe_pico.value = 0          # RP2040 never drives uio (avoid contention)
    tt.ui_in.value = ui_in
    tt.clock_project_PWM(fs)
    tt.reset_project(True)
    time.sleep_ms(2)
    tt.reset_project(False)
    time.sleep_ms(50)                 # let the CIC settle (> 2 frames)
    return tt


def capture(fs_out, path="/adc_raw.bin"):
    for p in (PIN_SDO, PIN_CSN, PIN_SCLK):
        Pin(p, Pin.IN)

    buf = bytearray(4 * N_WORDS)
    sm = rp2.StateMachine(SM_ID, spi_rx16, in_base=Pin(PIN_SDO))
    dma = rp2.DMA()
    ctrl = dma.pack_ctrl(size=2, inc_read=False, inc_write=True, treq_sel=DREQ_PIO1_RX0)
    dma.config(read=PIO1_RXF0, write=buf, count=N_WORDS, ctrl=ctrl, trigger=True)
    sm.active(1)

    timeout_ms = int(2000 * N_SAMPLES / fs_out) + 1000
    t0 = time.ticks_ms()
    while dma.active():
        if time.ticks_diff(time.ticks_ms(), t0) > timeout_ms:
            sm.active(0)
            dma.close()
            raise RuntimeError("timeout: no CS_N frames (check project select / clock / pins)")
        time.sleep_ms(10)
    sm.active(0)
    dma.close()

    with open(path, "wb") as f:
        f.write(buf)

    head = []
    for i in range(4):
        w = int.from_bytes(buf[4 * i:4 * i + 4], "little")
        for v in (w >> 16, w & 0xFFFF):
            head.append(v - 0x10000 if v & 0x8000 else v)
    print("saved", N_SAMPLES, "samples to", path, "first:", head)


# Example (BIAS=00, OSR=128, DBG=QUIET -> ui_in = 0x00; fs = 20 MHz):
#   setup_tt("tt_um_eleva_ccro_adc", 20_000_000, 0x00)
#   capture(20_000_000 / 128)
