import subprocess


class Run:
    @classmethod
    def dev(cls) -> None:
        """Start the dev server with auto-reload. Usage: uv run run_dev"""
        subprocess.run(["uvicorn", "main:app", "--reload"], check=True)

    @classmethod
    def test(cls) -> None:
        """Run the test suite. Usage: uv run run_test"""
        subprocess.run(["pytest"], check=True)

    @classmethod
    def prod(cls) -> None:
        """Start the production server. Usage: uv run run_prod"""
        subprocess.run(
            ["uvicorn", "main:app", "--workers", "4"],
            check=True,
        )
