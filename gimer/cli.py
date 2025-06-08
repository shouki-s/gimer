#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

import click
from rich.console import Console
from rich.prompt import Confirm

from gimer.git import Git
from gimer.repositories import get_github_repo_path

console = Console()

@click.command()
@click.argument('repo_url')
@click.argument('target_branch')
@click.argument('source_branch')
@click.option('--dry-run', is_flag=True, help='Show what would be done without actually doing it')
@click.option('--cleanup', is_flag=True, help='Remove local repository after completion')
def main(repo_url: str, target_branch: str, source_branch: str, dry_run: bool, cleanup: bool) -> None:
    repo_path = get_github_repo_path(repo_url)
    try:
        merge(repo_path, repo_url, target_branch, source_branch, dry_run)
    finally:
        if cleanup and repo_path:
            cleanup_repository(repo_path)

def merge(repo_path: Path, repo_url: str, target_branch: str, source_branch: str, dry_run: bool) -> None:
    """Merge a source branch into a target branch."""
    git = Git(dry_run=dry_run)
    os.chdir(repo_path)
    if not (repo_path / '.git').exists():
        console.print(f"⚡Cloning repository to {repo_path}")
        git.clone_repository_from_github(repo_url)

    if not git.check_working_directory_clean():
        console.print("⚡[yellow]Warning: You have uncommitted changes in the repository.[/yellow]")
        if not Confirm.ask("⚡Do you want to continue? It will clean dirty files and reset the repository."):
            return
        console.print("⚡Cleaning working directory...")
        git.clean_working_directory()
        console.print("⚡[green]Working directory cleaned.[/green]")

    console.print(f"\n⚡[bold]Starting merge:[/bold] {target_branch} ← {source_branch}")
    git.fetch()
    git.checkout_branch(source_branch)
    git.pull_branch(source_branch)
    git.checkout_branch(target_branch)
    git.pull_branch(target_branch)
    try:
        git.merge_branch(source_branch)
    except Exception as e:
        console.print("⚡[red]An error occurred during merge:[/red]")
        console.print(f"⚡{e!s}")
        if "CONFLICT" not in str(e):
            return
        console.print("\n⚡[yellow]Merge conflicts detected. Opening editor for conflict resolution...[/yellow]")
        git.resolve_conflicts()
        if not git.is_merge_in_progress():
            console.print("⚡[yellow]Merge was aborted. Exiting...[/yellow]")
            return
        git.commit_merge()

    console.print("⚡[green]Merge completed successfully![/green]")
    console.print(f"⚡Pushing {target_branch} to origin...")
    git.push_branch(target_branch)
    console.print("⚡[green]Push completed successfully![/green]")

def cleanup_repository(repo_path: str) -> None:
    """Remove local repository after completion."""
    console.print(f"⚡Removing local repository: [yellow]{repo_path}[/yellow]")
    os.chdir("..")  # 親ディレクトリに移動
    shutil.rmtree(repo_path)
    console.print("⚡[green]Local repository removed.[/green]")

if __name__ == '__main__':
    main()
