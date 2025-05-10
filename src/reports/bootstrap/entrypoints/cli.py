from click import Context, group, pass_context
from dishka.integrations.click import setup_dishka
from uvicorn import Server as UvicornServer

from reports.bootstrap.config import (
    get_alembic_config,
    get_hatchet_worker,
    get_uvicorn_config,
)
from reports.bootstrap.containers import bootstrap_cli_container
from reports.presentation.cli.migrations import (
    downgrade_migration,
    make_migrations,
    show_current_migration,
    upgrade_migration,
)
from reports.presentation.cli.server_starting import start_uvicorn
from reports.presentation.cli.worker import start_worker


@group()
@pass_context
def main(context: Context) -> None:
    alembic_config = get_alembic_config()
    uvicorn_config = get_uvicorn_config()
    uvicorn_server = UvicornServer(uvicorn_config)
    hatchet_worker = get_hatchet_worker()
    dishka_container = bootstrap_cli_container(
        alembic_config, uvicorn_config, uvicorn_server, hatchet_worker
    )
    setup_dishka(dishka_container, context, finalize_container=True)


main.command(start_uvicorn)
main.command(make_migrations)
main.command(upgrade_migration)
main.command(downgrade_migration)
main.command(show_current_migration)
main.command(start_worker)
