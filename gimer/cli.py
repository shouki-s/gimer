#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

import click
from rich.console import Console
from rich.prompt import Confirm

from gimer.git import Git, UserAbortedError
from gimer.repositories import get_github_repo_path

console = Console()

@click.command()
@click.argument('repo_url')
@click.argument('target_branch')
@click.argument('source_branch')
@click.option('--dry-run', is_flag=True, help='Show what would be done without actually doing it')
@click.option('--cleanup', is_flag=True, help='Remove local repository after completion')
@click.option('--confirm', is_flag=False, flag_value='origin', type=click.Choice(['origin', 'all']), help='Confirm before executing all or affecting origin git commands')
def main(repo_url: str, target_branch: str, source_branch: str, dry_run: bool, cleanup: bool, confirm: str | None) -> None:
    repo_path = get_github_repo_path(repo_url)
    try:
        config = {"dry_run": dry_run, "confirm": confirm}
        merge(repo_path, repo_url, target_branch, source_branch, config)
    except UserAbortedError:
        console.print("⚡[yellow]Operation cancelled.[/yellow]")
    finally:
        if cleanup and repo_path:
            cleanup_repository(repo_path)

def merge(repo_path: Path, repo_url: str, target_branch: str, source_branch: str, config: dict) -> None:
    """Merge a source branch into a target branch."""
    git = Git(**config)
    os.chdir(repo_path)
    console.print(f"⚡[bold]working directory:[/bold] {repo_path}")
    if not (repo_path / '.git').exists():
        git.clone_repository_from_github(repo_url)

    if not git.check_working_directory_clean():
        console.print("⚡[yellow]Warning: You have uncommitted changes in the repository.[/yellow]")
        if not Confirm.ask("⚡Do you want to continue? It will clean dirty files and reset the repository."):
            return
        git.clean_working_directory()

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

    git.push_branch(target_branch)
    console.print("⚡[green]Merge completed successfully![/green]")

def cleanup_repository(repo_path: str) -> None:
    """Remove local repository after completion."""
    os.chdir("..")  # 親ディレクトリに移動
    shutil.rmtree(repo_path)

if __name__ == '__main__':
    main()
