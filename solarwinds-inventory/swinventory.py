import string

from httpx import AsyncClient

from models import Credentials, Device


SW_HOST = "10.0.0.200"


async def query_sw(
    credentials: Credentials,
    query: str,
    parameters: dict = {},
) -> list[dict[str, int | str]]:
    headers = {"Content-Type": "application/json"}
    data = {
        "query": query,
    }
    if parameters:
        data["parameters"] = parameters

    async with AsyncClient(verify=False) as client:
        response = await client.post(
            url=f"https://{SW_HOST}:17778/SolarWinds/InformationService/v3/Json/Query",
            headers=headers,
            auth=(credentials.username, credentials.password),
            json=data,
        )
    if response.status_code != 200:
        return []
    return response.json()["results"]


def get_query_criteria(parameters: list = []) -> str | dict:
    query = f"""
        SELECT NodeID as nodeid, IPAddress as ip, NodeName as hostname
        FROM Orion.Nodes
    """
    parameters_dict = {}
    if parameters:
        parameters_dict = {
            string.ascii_lowercase[i]: p + "%" for i, p in enumerate(parameters)
        }
        query = (
            query
            + "WHERE "
            + "OR ".join(
                ["NodeName LIKE @" + str(pkey) + " " for pkey in parameters_dict.keys()]
            ).rstrip()
        )
    return query, parameters_dict


async def get_solarwinds_inventory(
    credentials: Credentials, criteria: list
) -> list[Device]:
    query, parameters = get_query_criteria(criteria)
    results = await query_sw(credentials, query, parameters)
    return [
        Device(
            nodeid=result["nodeid"],
            ip=result["ip"],
            hostname=result["hostname"],
            platform="cisco_iosxe",
        )
        for result in results
    ]
