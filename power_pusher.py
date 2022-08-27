from smbus2 import SMBus
import click


DEFAULT_POWER_ON_SECONDS = 0.5
DEFAULT_POWER_OFF_SECONDS = 5


# MCP23017 defs
IODIRA   = 0x00  # Pin direction register
IODIRB   = 0x01  # Pin direction register
IPOLA    = 0x02
IPOLB    = 0x03
GPINTENA = 0x04
GPINTENB = 0x05
DEFVALA  = 0x06
DEFVALB  = 0x07
INTCONA  = 0x08
INTCONB  = 0x09
IOCONA   = 0x0A
IOCONB   = 0x0B
GPPUA    = 0x0C
GPPUB    = 0x0D

INTFA    = 0x0E
INTFB    = 0x0F
INTCAPA  = 0x10
INTCAPB  = 0x11
GPIOA    = 0x12
GPIOB    = 0x13
OLATA    = 0x14
OLATB    = 0x15

BANK_BIT    = 7
MIRROR_BIT  = 6
SEQOP_BIT   = 5
DISSLW_BIT  = 4
HAEN_BIT    = 3
ODR_BIT     = 2
INTPOL_BIT  = 1

GPA0 = 0
GPA1 = 1
GPA2 = 2
GPA3 = 3
GPA4 = 4
GPA5 = 5
GPA6 = 6
GPA7 = 7
GPB0 = 8
GPB1 = 9
GPB2 = 10
GPB3 = 11
GPB4 = 12
GPB5 = 13
GPB6 = 14
GPB7 = 15


class PowerPusher:
    '''Pushes the power button through GPIO'''
    def __init__(self, *, bus, address=0x20):
        self.bus = bus
        self.address = address

    def __enter__(self):
        return PowerPusher._SynchronousSession(self)

    def __aenter__(self):
        return PowerPusher._AsynchronousSession(self)

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __aexit__(self, exc_type, exc_value, traceback):
        pass

    def _setup_pins(self):
        # set all outputs low
        self.bus.write_byte_data(
            self.address,
            OLATA,
            0x00,  # GPA: 7, 6, 5, 4, 3, 2, 1, 0
                   # VAL: 0, 0, 0, 0, 0, 0, 0, 0
        )

        # set first 4 GPA ports to outputs, rest to inputs
        self.bus.write_byte_data(
            self.address,
            IODIRA,
            0xF0,  # GPA: 7, 6, 5, 4, 3, 2, 1, 0
                   # VAL: 1, 1, 1, 1, 0, 0, 0, 0
                   # I/O: I, I, I, I, O, O, O, O
        )

        # set all GPB ports to inputs
        self.bus.write_byte_data(
            self.address,
            IODIRB,
            0xFF,  # GPB: 7, 6, 5, 4, 3, 2, 1, 0
                   # VAL: 1, 1, 1, 1, 1, 1, 1, 1
                   # I/O: I, I, I, I, I, I, I, I
        )

    class _Session:
        def __init__(self, pusher):
            self._pusher = pusher

    class _AsynchronousSession(_Session):
        async def power_on(self, *, index, hold_seconds=DEFAULT_POWER_ON_SECONDS,):
            raise NotImplementedError()

        async def power_off(self, *, index, hold_seconds=DEFAULT_POWER_OFF_SECONDS,):
            raise NotImplementedError()

    class _SynchronousSession(_Session):
        def power_hold(self, *, index, hold_seconds):
            return self._pusher.power_hold(
                index=index,
                hold_seconds=hold_seconds,
            )

        def power_on(self, *, index, hold_seconds=DEFAULT_POWER_ON_SECONDS,):
            return self._pusher.power_on(
                index=index,
                hold_seconds=hold_seconds,
            )

        def power_off(self, *, index, hold_seconds=DEFAULT_POWER_OFF_SECONDS,):
            return self._pusher.power_off(
                index=index,
                hold_seconds=hold_seconds,
            )

    def _power_hold(self, *, index, hold_seconds, waiter,):
        if index < 0:
            raise ValueError("index may not be < 0")
        elif index > 4:
            raise ValueError("index may not be > 4")

        # get original value
        value0 = self.bus.read_byte_data(self.address, OLATA)

        if index in range(3):
            pass

        elif index in (3, 4):
            bitmask = 0x01 << (index - 1)

        else:
            raise ValueError(f'%r is an invalid index')

        # calculate the appropriate bits for "enable"
        value_enable = (value0 | bitmask)
        # calculate the appropriate bits for "disable"
        value_disable = (value0 & ~bitmask)

        # write to the output (start the hold)
        self.bus.write_byte_data(self.address, OLATA, value_enable,)

        # call the waiter while we hold down
        waiter()

        # write to the output (stop the hold)
        self.bus.write_byte_data(self.address, OLATA, value_disable,)

    def power_hold(self, *, index, hold_seconds,):
        self._power_hold(
            index=index,
            hold_seconds=hold_seconds,
            waiter=lambda hold_seconds: time.sleep(hold_seconds),
        )

    def power_on(self, *, index, hold_seconds=DEFAULT_POWER_ON_SECONDS,):
        self._power_hold(
            index=index,
            hold_seconds=hold_seconds,
            waiter=lambda hold_seconds: time.sleep(hold_seconds),
        )

    def power_off(self, *, index, hold_seconds=DEFAULT_POWER_OFF_SECONDS,):
        self._power_hold(
            index=index,
            hold_seconds=hold_seconds,
            waiter=lambda hold_seconds: time.sleep(hold_seconds),
        )


def power_hold(*, index, hold_seconds,):
    with SMBus(1) as bus:
        with PowerPusher(bus = bus) as pusher:
            pusher.power_hold(
                index=index,
                hold_seconds=hold_seconds,
            )


def power_on(*, index, hold_seconds=DEFAULT_POWER_ON_SECONDS,):
    power_hold(
        index=index,
        hold_seconds=hold_seconds,
    )


def power_off(*, index, hold_seconds=DEFAULT_POWER_OFF_SECONDS,):
    power_hold(
        index=index,
        hold_seconds=hold_seconds,
    )


@click.group()
def cli():
    pass


@cli.command('power-hold')
@click.option(
    '--index',
    type=int,
    help='index for which to hold power',
    required=True,
)
@click.option(
    '--hold-seconds',
    type=float,
    help='how many seconds to "hold the power button down"',A
    required=True,
)
def cli_power_hold(index, hold_seconds):
    power_hold(
        index=index,
        hold_seconds=hold_seconds,
    )


@cli.command('power-on')
@click.option(
    '--index',
    type=int,
    help='index for which to hold power',
    required=True,
)
@click.option(
    '--hold-seconds',
    type=float,
    help='how many seconds to "hold the power button down"',
    default=DEFAULT_POWER_ON_SECONDS,
)
def cli_power_on(index, hold_seconds):
    power_hold(
        index=index,
        hold_seconds=hold_seconds,
    )


@cli.command('power-off')
@click.option(
    '--index',
    type=int,
    help='index for which to hold power',
    required=True,
)
@click.option(
    '--hold-seconds',
    type=float,
    help='how many seconds to "hold the power button down"',
    default=DEFAULT_POWER_OFF_SECONDS,
)
def cli_power_off(index, hold_seconds):
    power_hold(
        index=index,
        hold_seconds=hold_seconds,
    )


if __name__ == '__main__':
    cli()
