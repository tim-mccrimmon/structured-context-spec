"""
Commit command - commit one workspace's changes (D-84)
"""

import tempfile
from pathlib import Path

import click
from scs_validator.envelope import Change, relative
from scs_validator.gitrepo import GitRepo, GitUnavailable

from scs_tools import git, identity
from scs_tools.machine import EXIT_USAGE, CommandError, machine_command
from scs_tools.versioning import PERSON_RE
from scs_tools.workspace import repository_root, select_workspace


def _author(given):
    """The commit's author: a person the user names, never taken from git (D-13)."""
    author = (given or "").strip()
    if not author:
        suggested = identity.person_suggestion()
        raise CommandError(
            "COMMIT_AUTHOR_REQUIRED",
            "A commit needs an author: pass --author 'Name <email>'. It is never taken from "
            "git configuration",
            exit_code=EXIT_USAGE,
            suggestion={"author": suggested} if suggested else None,
        )
    if not PERSON_RE.match(author) or author.startswith("role:"):
        raise CommandError(
            "COMMIT_AUTHOR_INVALID",
            f"The author must be a person identifier, Name <email>; got '{author}'",
            exit_code=EXIT_USAGE,
        )
    return author


def _git_top(workspace: Path) -> Path:
    if not git.available():
        raise CommandError("GIT_REQUIRED", "scs commit needs git, and git was not found")
    try:
        found = GitRepo.find(workspace)
    except GitUnavailable as e:
        raise CommandError("GIT_REQUIRED", f"scs commit needs git: {e}")
    if found is None:
        raise CommandError("GIT_REQUIRED", f"{workspace} is not in a git repository")
    return found.toplevel


@click.command()
@click.option("--message", "-m", required=True, help="The commit message")
@click.option("--author", default=None, help="Who made the changes: Name <email>")
@click.option(
    "--workspace", default=None, help="Workspace: domain or a Project name (default: current)"
)
@click.option("--dry-run", is_flag=True, help="Report what would be committed; commit nothing")
@machine_command("commit")
def commit(envelope, out, message, author, workspace, dry_run):
    """
    Commit one workspace's changes

    Commits the workspace's changed and new files, and nothing outside it: changes elsewhere in
    the repository, staged or not, stay as they are. The author is the person you name; the
    committer is scs-tools. Ignored files, such as source documents in sources/, are never
    committed. Versions are committed by 'scs bundle version', not by this command.

    \b
    Examples:
        scs commit --workspace domain -m "Draft data handling rules" \\
            --author "Jane Doe <jane@acme-health.org>" --dry-run
        scs commit -m "Record intake answers" --author "Jane Doe <jane@acme-health.org>"
    """
    if not message.strip():
        raise CommandError("INPUT_EMPTY", "The commit message is empty", exit_code=EXIT_USAGE)
    author = _author(author)
    path = select_workspace(workspace).resolve()
    root = repository_root(path) or path
    top = _git_top(path)
    pathspec = [relative(path, top)]

    def shown(paths):
        return [{"path": relative(top / p["path"], root), "status": p["status"]} for p in paths]

    pending = git.pending_paths(top, pathspec)
    envelope.result = {"workspace": relative(path, root), "files": len(pending)}
    if not pending:
        out.echo("Nothing to commit")
        return
    if dry_run:
        envelope.changes.append(Change("git-commit", ref="HEAD", paths=shown(pending)))
        out.echo(f"Would commit {len(pending)} file(s) in {relative(path, root)} as {author}")
        return

    old = git.head(top)
    try:
        with tempfile.TemporaryDirectory(prefix="scs-commit-") as work:
            new = git.commit_paths(top, pathspec, message, author, Path(work))
        git.move_head(top, new, old, "scs commit")
        git.sync_index(top, pathspec)
    except git.GitError as e:
        raise CommandError("GIT_COMMAND_FAILED", f"{e}; nothing was committed")
    envelope.changes.append(
        Change("git-commit", ref=new, paths=shown(git.committed_paths(top, new)))
    )
    out.echo(f"Committed {len(pending)} file(s) in {relative(path, root)} ({new[:7]})")
