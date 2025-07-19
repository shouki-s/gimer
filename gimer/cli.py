#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

import click
from github import Github
from InquirerPy import inquirer
from rich.console import Console
from rich.prompt import Confirm

from gimer.git import Git, UserAbortedError
from gimer.i18n import _
from gimer.repositories import get_github_repo_path

console = Console()
token = os.environ.get("GITHUB_TOKEN")
gh = Github(token) if token else Github()

@click.command()
@click.argument('repo_url')
@click.option('--source', help='Source branch to merge from')
@click.option('--target', help='Target branch to merge into')
@click.option('--dry-run', is_flag=True, help='Show what would be done without actually doing it')
@click.option('--cleanup', is_flag=True, help='Remove local repository after completion')
@click.option('-y', '--no-confirm', is_flag=True, help="Do not confirm before executing git commands")
@click.option('--confirm-all', is_flag=True, help="Confirm before executing all git commands")
def main(  # noqa: PLR0913
    repo_url: str,
    source: str | None,
    target: str | None,
    dry_run: bool,
    cleanup: bool,
    no_confirm: bool,
    confirm_all: bool,
) -> None:
    repo_path = get_github_repo_path(repo_url)
    try:
        config = {"dry_run": dry_run, "no_confirm": no_confirm, "confirm_all": confirm_all}
        merge(repo_path, repo_url, target, source, config)
    except UserAbortedError:
        console.print(f"⚡[yellow]{_('Operation cancelled.')}[/yellow]")
    finally:
        if cleanup and repo_path:
            cleanup_repository(repo_path)

def merge(repo_path: Path, repo_url: str, target_branch: str | None, source_branch: str | None, config: dict) -> None:
    """Merge a source branch into a target branch."""
    git = Git(**config)
    os.chdir(repo_path)
    if not (repo_path / '.git').exists():
        git.clone_repository(repo_url)

    if not git.check_working_directory_clean():
        console.print(f"⚡[yellow]{_('Warning: You have uncommitted changes in the repository.')}[/yellow]")
        if not Confirm.ask(f"⚡{_('Do you want to continue? It will clean dirty files and reset the repository.')}"):
            return
        git.clean_working_directory()

    git.fetch()
    branches = git.get_branches()
    if not source_branch:
        source_branch = inquirer.fuzzy(
            _("Select source branch to merge from"),
            choices=branches,
        ).execute()
    if not target_branch:
        target_branch = inquirer.fuzzy(
            _("Select target branch to merge into"),
            choices=branches,
        ).execute()
    if not (config["no_confirm"] or Confirm.ask(f"⚡{_('Do you want to git merge {0} ← {1}?').format(target_branch, source_branch)}", default=True)):
        return
    git.checkout_branch(source_branch)
    git.pull_branch(source_branch)
    git.checkout_branch(target_branch)
    git.pull_branch(target_branch)
    try:
        git.merge_branch(source_branch)
    except Exception as e:
        console.print(f"⚡[red]{_('An error occurred during merge:')}[/red]")
        console.print(f"⚡{e!s}")
        if "CONFLICT" not in str(e):
            return
        console.print(f"\n⚡[yellow]{_('Merge conflicts detected.')}[/yellow]")
        if config["no_confirm"] or not Confirm.ask(f"⚡{_('Do you want to resolve conflicts manually?')}", default=True):
            git.abort_merge()
            return
        git.resolve_conflicts()
        if not git.is_merge_in_progress():
            console.print(f"⚡[yellow]{_('Merge was aborted. Exiting...')}[/yellow]")
            return
        git.commit_merge()

    git.push_branch(target_branch)
    console.print(f"⚡[green]{_('Merge completed successfully!')}[/green]")

def cleanup_repository(repo_path: Path) -> None:
    """Remove local repository after completion."""
    os.chdir("..")  # move to parent directory before removing
    console.print(f"⚡[bold]{_('Removing...')}[/bold] {repo_path}")
    shutil.rmtree(repo_path)

if __name__ == '__main__':
    main()
