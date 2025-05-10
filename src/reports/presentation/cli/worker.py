import asyncio
from signal import SIGINT, signal

from dishka import FromDishka
from dishka.integrations.click import inject
from hatchet_sdk import Worker


@inject
def start_worker(*, worker: FromDishka[Worker]) -> None:
    signal(SIGINT, lambda *_: asyncio.create_task(worker.exit_gracefully()))

    worker.start()
