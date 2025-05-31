#!/usr/bin/env python3
import click
import git
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
import sys

console = Console()

def get_current_branch(repo):
    return repo.active_branch.name

def get_all_branches(repo):
    return [branch.name for branch in repo.branches]

def check_working_directory_clean(repo):
    return not repo.is_dirty()

@click.command()
def main():
    """CLI tool to make Git merge operations easier"""
    try:
        repo = git.Repo('.')
    except git.InvalidGitRepositoryError:
        console.print("[red]Error: This directory is not a Git repository.[/red]")
        sys.exit(1)

    # Show current branch
    current_branch = get_current_branch(repo)
    console.print(f"\n[bold]Current branch:[/bold] [green]{current_branch}[/green]")

    # Check if working directory is clean
    if not check_working_directory_clean(repo):
        console.print("[yellow]Warning: You have uncommitted changes in your working directory.[/yellow]")
        if not Confirm.ask("Do you want to continue?"):
            sys.exit(0)

    # Show mergeable branches
    branches = get_all_branches(repo)
    branches.remove(current_branch)

    table = Table(title="Mergeable Branches")
    table.add_column("No.", style="cyan")
    table.add_column("Branch Name", style="green")

    for i, branch in enumerate(branches, 1):
        table.add_row(str(i), branch)

    console.print(table)

    # Select branch to merge
    branch_num = Prompt.ask(
        "Select a branch number to merge",
        choices=[str(i) for i in range(1, len(branches) + 1)]
    )
    target_branch = branches[int(branch_num) - 1]

    # Execute merge
    try:
        console.print(f"\n[bold]Starting merge:[/bold] {current_branch} ← {target_branch}")
        repo.git.merge(target_branch)
        console.print("[green]Merge completed successfully![/green]")
    except git.GitCommandError as e:
        console.print("[red]An error occurred during merge:[/red]")
        console.print(str(e))
        if "CONFLICT" in str(e):
            console.print("\n[yellow]Merge conflicts detected. Please resolve them manually.[/yellow]")
        sys.exit(1)

if __name__ == '__main__':
    main() 