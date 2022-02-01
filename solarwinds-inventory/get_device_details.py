import asyncio
from argparse import ArgumentParser
from operator import attrgetter

from scrapli import AsyncScrapli
from rich import box
from rich.console import Console
from rich.table import Table

from models import Credentials, Device
from swinventory import get_solarwinds_inventory


async def get_device_version(device: Device, credentials: Credentials) -> None:
    connection = AsyncScrapli(
        host=str(device.ip),
        auth_username=credentials.username,
        auth_password=credentials.password,
        auth_strict_key=False,
        transport="asyncssh",
        platform=device.platform,
    )

    async with connection as conn:
        result = await conn.send_command("show version")

    result = result.textfsm_parse_output()[0]
    device.serial = result["serial"][0]
    device.version = result["version"]


def print_results(devices: list[Device]):
    console = Console()
    table = Table(show_header=True, box=box.MINIMAL_HEAVY_HEAD)
    table.add_column("Hostname")
    table.add_column("IP Address")
    table.add_column("Serial")
    table.add_column("Version")

    devices.sort(key=attrgetter("ip"))
    for device in devices:
        table.add_row(device.hostname, str(device.ip), device.serial, device.version)
    console.print(table)


async def main() -> None:
    parser = ArgumentParser(description="Solarwinds SOT")
    parser.add_argument("-u", "--username", help="Username")
    parser.add_argument("-p", "--password", help="Password")
    parser.add_argument(
        "-c",
        "--criteria",
        help="Device search criteria. Must be comma separated values",
    )
    args = parser.parse_args()

    credentials = Credentials(username=args.username, password=args.password)
    criteria = args.criteria.split(",") if args.criteria else None
    devices = await get_solarwinds_inventory(credentials, criteria)

    if devices:
        for device in devices:
            await get_device_version(device, credentials)
        print_results(devices)


if __name__ == "__main__":
    asyncio.run(main())
