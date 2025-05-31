#!/usr/bin/env python3
import sys
from typing import List

import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

from .git_utils import (
    get_repository,
    get_current_branch,
    get_all_branches,
    check_working_directory_clean,
    merge_branch,
    NotGitRepositoryError,
    MergeError,
)
from .constants import (
    TABLE_TITLE,
    COLUMN_NUMBER,
    COLUMN_BRANCH,
    MSG_CURRENT_BRANCH,
    MSG_WARNING_UNCOMMITTED,
    MSG_CONTINUE,
    MSG_SELECT_BRANCH,
    MSG_STARTING_MERGE,
    MSG_MERGE_SUCCESS,
    MSG_MERGE_ERROR,
    MSG_MERGE_CONFLICT,
)

console = Console()

def display_branches(branches: List[str]) -> None:
    table = Table(title=TABLE_TITLE)
    table.add_column(COLUMN_NUMBER, style="cyan")
    table.add_column(COLUMN_BRANCH, style="green")

    for i, branch in enumerate(branches, 1):
        table.add_row(str(i), branch)

    console.print(table)

@click.command()
def main() -> None:
    try:
        repo = get_repository()
    except NotGitRepositoryError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

    current_branch = get_current_branch(repo)
    console.print(f"\n[bold]{MSG_CURRENT_BRANCH}[/bold] [green]{current_branch}[/green]")

    if not check_working_directory_clean(repo):
        console.print(f"[yellow]{MSG_WARNING_UNCOMMITTED}[/yellow]")
        if not Confirm.ask(MSG_CONTINUE):
            sys.exit(0)

    branches = get_all_branches(repo)
    branches.remove(current_branch)
    display_branches(branches)

    branch_num = Prompt.ask(
        MSG_SELECT_BRANCH,
        choices=[str(i) for i in range(1, len(branches) + 1)]
    )
    target_branch = branches[int(branch_num) - 1]

    try:
        console.print(f"\n[bold]{MSG_STARTING_MERGE}[/bold] {current_branch} ← {target_branch}")
        merge_branch(repo, target_branch)
        console.print(f"[green]{MSG_MERGE_SUCCESS}[/green]")
    except MergeError as e:
        console.print(f"[red]{MSG_MERGE_ERROR}[/red]")
        console.print(str(e))
        if "CONFLICT" in str(e):
            console.print(f"\n[yellow]{MSG_MERGE_CONFLICT}[/yellow]")
        sys.exit(1)

if __name__ == '__main__':
    main()
