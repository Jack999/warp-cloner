import random
from typing import Any, TypedDict
from itertools import count

from aiohttp import ClientResponse, ClientSession, ClientTimeout
from aiohttp_socks import ProxyConnector

from config import config


BASE_URL: str = "https://api.cloudflareclient.com"
BASE_HEADERS: dict[str, str] = {
    'User-Agent': 'okhttp/3.12.1',
}

PROXY_COUNTER = iter(count())


class RegisterDataAccount(TypedDict):
    id: str
    account_type: str
    created: str # date in ISO 8601 format
    updated: str # date in ISO 8601 format
    premium_data: int
    quota: int
    usage: int
    warp_plus: int
    refferal_count: int
    referral_renewal_countdown: int
    role: str
    license: str


class RegisterData(TypedDict):
    id: str
    type: str
    name: str
    key: str # base64 encoded
    account: RegisterDataAccount
    config: Any # we don't use it, so i think it's acceptable to use any
    token: str
    warp_enabled: bool
    waitlist_enabled: bool
    created: str # date in ISO 8601 format
    updated: str # date in ISO 8601 format
    tos: str # date in ISO 8601 format
    place: int
    locale: str
    enabled: bool
    install_id: str
    fcm_token: str


class GetInfoData(TypedDict):
    id: str
    account_type: str
    created: str # date in ISO 8601 format
    updated: str # date in ISO 8601 format
    premium_data: int
    quota: int
    warp_plus: bool
    referral_count: int
    referral_renewal_countdown: int
    role: str
    license: str


async def register(path: str, session: ClientSession, data: dict[str, str] = {}) -> RegisterData:
    response: ClientResponse = await session.post(
        '/{}/reg'.format(path),
        headers={
            'Content-Type': 'application/json; charset=UTF-8',
            **BASE_HEADERS,
        },
        json=data
    )

    if response.status != 200:
        response.close()
        raise Exception('Failed to register: {} {}'.format(response.status, await response.text()))

    json: RegisterData = await response.json()

    return json


async def add_key(path: str, session: ClientSession, reg_id: str, token: str, key: str) -> None:
    response: ClientResponse = await session.put(
        '/{}/reg/{}/account'.format(path, reg_id),
        headers={
            'Authorization': 'Bearer {}'.format(token),
            'Content-Type': 'application/json; charset=UTF-8',
            **BASE_HEADERS,
        },
        json={
            'license': key,
        }
    )

    if response.status != 200:
        response.close()
        raise Exception('Failed to add key: {}'.format(response.status))


async def delete_account(path: str, session: ClientSession, reg_id: str, token: str) -> None:
    response: ClientResponse = await session.delete(
        '/{}/reg/{}'.format(path, reg_id),
        headers={
            'Authorization': 'Bearer {}'.format(token),
            **BASE_HEADERS,
        }
    )

    if response.status != 204:
        response.close()
        raise Exception('Failed to delete account: {}'.format(response.status))


async def get_account(path: str, session: ClientSession, reg_id: str, token: str) -> GetInfoData:
    response: ClientResponse = await session.get(
        '/{}/reg/{}/account'.format(path, reg_id),
        headers={
            'Authorization': 'Bearer {}'.format(token),
            **BASE_HEADERS,
        }
    )

    if response.status != 200:
        response.close()
        raise Exception('Failed to get account: {}'.format(response.status))

    json: GetInfoData = await response.json()

    return json


async def clone_key(key: str) -> GetInfoData:
    proxies: list[str] = [] if config.PROXY_URL is None else config.PROXY_URL.split(',')

    proxy_url: str | None = proxies[next(PROXY_COUNTER) % len(proxies)] if config.PROXY_URL else None

    connector: ProxyConnector | None = ProxyConnector.from_url(
        proxy_url
    ) if proxy_url else None

    path: str = 'v0a{}'.format(
        random.randint(100, 999)
    )

    base_url: str = BASE_URL

    timeout: ClientTimeout = ClientTimeout(total=15)

    session = ClientSession(connector=connector, timeout=timeout, base_url=base_url)


    try:
        register_data: RegisterData = await register(path, session)

        refferer_body: dict[str, str] = {
            'referrer': register_data['id'],
        }

        await register(path, session, refferer_body)

        await add_key(path, session, register_data['id'], register_data['token'], key)
        await add_key(path, session, register_data['id'], register_data['token'], register_data['account']['license'])

        information: GetInfoData = await get_account(path, session, register_data['id'], register_data['token'])

        await delete_account(path, session, register_data['id'], register_data['token'])

        return information
    finally:
        await session.close()
        if connector is not None:
            await connector.close()
