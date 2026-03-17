import subprocess
import sys


class Db:
    @classmethod
    def generate(cls) -> None:
        """Run alembic autogenerate revision. Usage: uv run db_generate <message>"""
        message = sys.argv[1] if len(sys.argv) > 1 else "migration"
        subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", message],
            check=True,
        )

    @classmethod
    def migrate(cls) -> None:
        """Run alembic upgrade head. Usage: uv run db_migrate"""
        subprocess.run(["alembic", "upgrade", "head"], check=True)

    @classmethod
    def revert(cls) -> None:
        """Downgrade the last migration. Usage: uv run db_revert"""
        subprocess.run(["alembic", "downgrade", "-1"], check=True)
