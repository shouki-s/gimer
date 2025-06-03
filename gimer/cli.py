#!/usr/bin/env python3
import os
import sys

import click
from rich.console import Console
from rich.prompt import Confirm

from .git_utils import (
    check_working_directory_clean,
    clone_repository_from_github,
    get_repository,
    merge_branch,
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
    repo = get_repository()

    if not check_working_directory_clean(repo):
        console.print("[yellow]Warning: You have uncommitted changes in your working directory.[/yellow]")
        if not Confirm.ask("Do you want to continue?"):
            sys.exit(0)

    try:
        console.print(f"\n[bold]Starting merge:[/bold] {target_branch} ← {source_branch}")
        repo.git.checkout(target_branch)
        merge_branch(repo, source_branch)
        console.print("[green]Merge completed successfully![/green]")
    except Exception as e:
        console.print("[red]An error occurred during merge:[/red]")
        console.print(str(e))
        if "CONFLICT" in str(e):
            console.print("\n[yellow]Merge conflicts detected. Please resolve them manually.[/yellow]")
        sys.exit(1)

if __name__ == '__main__':
    main()
