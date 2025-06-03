#!/usr/bin/env python3
import os
import sys

import click
from rich.console import Console
from rich.prompt import Confirm

from .git_utils import (
    check_working_directory_clean,
    checkout_branch,
    clean_working_directory,
    clone_repository_from_github,
    get_repository,
    merge_branch,
    push_branch,
)
from .repositories import get_github_repo_path

console = Console()

@click.command()
@click.argument('repo_url')
@click.argument('source_branch')
@click.argument('target_branch')
def main(repo_url: str, source_branch: str, target_branch: str) -> None:
    repo_path = get_github_repo_path(repo_url)
    if not (repo_path / '.git').exists():
        console.print(f"Cloning repository to {repo_path}")
        clone_repository_from_github(repo_url, str(repo_path))

    os.chdir(repo_path)
    get_repository()

    if not check_working_directory_clean():
        console.print("[yellow]Warning: You have uncommitted changes in the repository.[/yellow]")
        if Confirm.ask("Do you want to continue? It will clean dirty files and reset the repository."):
            console.print("Cleaning working directory...")
            clean_working_directory()
            console.print("[green]Working directory cleaned.[/green]")
        else:
            return

    console.print(f"\n[bold]Starting merge:[/bold] {target_branch} ← {source_branch}")
    checkout_branch(target_branch)
    try:
        merge_branch(source_branch)
    except Exception as e:
        console.print("[red]An error occurred during merge:[/red]")
        console.print(str(e))
        if "CONFLICT" in str(e):
            console.print(
                "\n[yellow]Merge conflicts detected. Please resolve them manually.[/yellow]"
            )
        return

    console.print("[green]Merge completed successfully![/green]")
    console.print(f"Pushing {target_branch} to origin...")
    push_branch(target_branch)
    console.print("[green]Push completed successfully![/green]")


if __name__ == '__main__':
    main()
