"""CLI entry point for PersonaGym."""

import typer
import asyncio
import os
import sys


sys.path.append(os.getcwd())

from src.green_agent import start_green_agent
from src.white_agent import start_white_agent

from src.launcher import launch_evaluation

app = typer.Typer(help="PersonaGym Framework")

@app.command()
def green(port: int = 9001):
    """Start the green agent."""
    start_green_agent(host="127.0.0.1", port=port)

@app.command()
def white(port: int = 9002):
    """Start the white agent."""
    start_white_agent(host="127.0.0.1", port=port)

@app.command()
def launch():
    """🚀 Launch the full local evaluation workflow."""
    asyncio.run(launch_evaluation())

if __name__ == "__main__":
    app()