import typer

from src.core.async_typer import AsyncTyper
from src.core.configs import get_settings
from src.core.providers.factory import make_container


class CLIFactory:
    def make(self) -> typer.Typer:
        settings = get_settings()
        container = make_container(settings)

        app = AsyncTyper(
            rich_markup_mode="rich",
            context_settings={
                "obj": {
                    "container": container,
                    "settings": settings,
                },
            },
        )

        self.add_reviews_scraper_command(app)
        self.add_abc_scraper_command(app)

        return app

    def add_reviews_scraper_command(self, app: typer.Typer) -> None:
        @app.command()
        async def reviews(ctx: typer.Context) -> None:
            """[green]Run[/green] scrape reviews."""
            raise NotImplementedError

    def add_abc_scraper_command(self, app: typer.Typer) -> None:
        @app.command()
        async def abc(ctx: typer.Context) -> None:
            """[green]Run[/green] scrape ...."""
            raise NotImplementedError
