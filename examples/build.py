"""Build the example Domain repositories with the engine, or check that they are current.

Each example directory holds a recipe.yaml and the repository it produces, checked in without
its .git directory. The build scaffolds the repository with `scs new`, adds the recipe's new
concepts with `scs add bundle --new`, retires every template
SCD the checked-in repository does not have, writes the ones it does with `scs scd write`,
records the intake, commits, releases each workspace with `scs bundle release`, and compiles
the released versions into dist/. SOURCE_DATE_EPOCH and the git dates are fixed to the
recipe's date, so the same engine produces the same bytes.

    python examples/build.py                 # rebuild every example in place
    python examples/build.py --check         # exit 1 if a rebuild differs from what is checked in
    python examples/build.py --keep DIR      # also keep each built repository, with its git
                                             # history and version tags, under DIR
"""

import argparse
import difflib
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import yaml

EXAMPLES = Path(__file__).resolve().parent


def scs_command() -> list[str]:
    beside = Path(sys.executable).parent / "scs"
    found = str(beside) if beside.exists() else shutil.which("scs")
    if not found:
        sys.exit("scs not found: install tools/cli (pip install -e tools/cli)")
    return [found]


def environment(date: str, home: Path) -> dict[str, str]:
    stamp = datetime.fromisoformat(date)
    git_date = stamp.strftime("%Y-%m-%dT%H:%M:%S+0000")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(
        SOURCE_DATE_EPOCH=str(int(stamp.timestamp())),
        GIT_AUTHOR_DATE=git_date,
        GIT_COMMITTER_DATE=git_date,
        GIT_CONFIG_NOSYSTEM="1",
        GIT_CONFIG_GLOBAL=str(home / "gitconfig"),
        HOME=str(home),
    )
    (home / "gitconfig").write_text(
        "[init]\n\tdefaultBranch = main\n[maintenance]\n\tauto = false\n[gc]\n\tauto = 0\n"
    )
    return env


class Builder:
    def __init__(self, recipe: dict, sources: Path, work: Path):
        self.recipe = recipe
        self.sources = sources
        self.env = environment(recipe["date"], work)
        self.repo = work / recipe["repository"]
        self.scs = scs_command()
        self.author = recipe["author"]
        self.name, self.email = self.author.rstrip(">").split(" <")

    def run(self, cwd: Path, *args: str, stdin: str | None = None) -> None:
        done = subprocess.run(
            [*self.scs, *args],
            cwd=cwd,
            env=self.env,
            input=stdin,
            capture_output=True,
            text=True,
            check=False,
        )
        if done.returncode != 0:
            sys.exit(f"scs {' '.join(args)} failed in {cwd}:\n{done.stdout}{done.stderr}")

    def build(self) -> Path:
        identity = ["--author", self.name, "--email", self.email, "--no-interactive"]
        domain = self.recipe["domain"]
        self.run(self.repo.parent, "new", "domain", *domain["new"], *identity)
        self.workspace(self.repo / "domain", "domain", domain)
        for project, spec in (self.recipe.get("projects") or {}).items():
            self.run(self.repo, "new", "project", *spec["new"], *identity)
            self.workspace(self.repo / "projects" / project, project, spec)
        return self.repo

    def workspace(self, root: Path, name: str, spec: dict) -> None:
        relative = root.relative_to(self.repo)
        authored = {
            p.name: p.read_text()
            for p in (self.sources / relative / "context" / "project").glob("*.yaml")
        }
        for concept in spec.get("concepts") or []:
            self.run(
                root,
                "add",
                "bundle",
                concept["name"],
                "--new",
                "--title",
                concept["title"],
                "--description",
                concept["description"],
                "--owner",
                concept["owner"],
                "--author",
                self.name,
                "--email",
                self.email,
            )
        retire = []
        for template in sorted((root / "context" / "project").glob("*.yaml")):
            if template.name not in authored:
                retire.append(yaml.safe_load(template.read_text())["id"])
        if retire:
            self.run(root, "bundle", "remove-scd", *retire)
        for file, text in sorted(authored.items()):
            self.run(
                root, "scd", "write", f"context/project/{file}", "--from-file", "-", stdin=text
            )
        for field, value in (spec.get("intake") or {}).items():
            for item in value if isinstance(value, list) else [value]:
                text = str(item).lower() if isinstance(item, bool) else str(item)
                self.run(root, "intake", "set", field, text)
        self.run(root, "commit", "-m", f"Draft the {name} workspace", "--author", self.author)
        release = spec["release"]
        version = release["version"]
        concepts = sorted(p.stem for p in (root / "bundles" / "concepts").glob("*.yaml"))
        self.run(
            root,
            "bundle",
            "release",
            "--version",
            version,
            *[a for c in concepts for a in ("--concept", f"{c}={version}")],
            "--approved-by",
            release["approved_by"],
            "--notes",
            release["notes"],
        )
        root_bundle = "domain-bundle.yaml" if name == "domain" else "project-bundle.yaml"
        self.run(root, "compile", f"bundles/{root_bundle}", "--version", version)
        self.run(
            root,
            "commit",
            "-m",
            f"Add the compiled artifact for {name} {version}",
            "--author",
            self.author,
        )


def tracked(repo: Path) -> dict[str, bytes]:
    files = (
        subprocess.run(["git", "ls-files", "-z"], cwd=repo, capture_output=True, check=True)
        .stdout.decode()
        .split("\0")
    )
    return {f: (repo / f).read_bytes() for f in files if f}


def checked_in(root: Path) -> dict[str, bytes]:
    return {
        str(p.relative_to(root)): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file() and ".git" not in p.relative_to(root).parts
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="compare; write nothing")
    parser.add_argument("--keep", type=Path, help="keep the built repositories here")
    parser.add_argument("examples", nargs="*", help="example directories (default: all)")
    args = parser.parse_args()

    dirs = [EXAMPLES / e for e in args.examples] or sorted(
        p.parent for p in EXAMPLES.glob("*/recipe.yaml")
    )
    stale = []
    for example in dirs:
        recipe = yaml.safe_load((example / "recipe.yaml").read_text())
        target = example / recipe["repository"]
        with tempfile.TemporaryDirectory() as tmp:
            sources = Path(tmp) / "sources"
            shutil.copytree(target, sources)
            work = Path(tmp) / "work"
            work.mkdir()
            repo = Builder(recipe, sources, work).build()
            built = tracked(repo)
            if args.keep:
                shutil.copytree(repo, args.keep / recipe["repository"], dirs_exist_ok=True)
            if args.check:
                have = checked_in(target)
                differ = sorted(f for f in set(built) | set(have) if built.get(f) != have.get(f))
                if differ:
                    stale.append(example.name)
                    print(f"{example.name}: differs from a rebuild:", *differ, sep="\n  ")
                    for f in differ:
                        old = have.get(f, b"").decode(errors="replace").splitlines()
                        new = built.get(f, b"").decode(errors="replace").splitlines()
                        diff = difflib.unified_diff(old, new, f"checked-in/{f}", f"rebuilt/{f}")
                        print(*list(diff)[:40], sep="\n")
                else:
                    print(f"{example.name}: current")
            else:
                shutil.rmtree(target)
                for f, data in built.items():
                    out = target / f
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(data)
                print(f"{example.name}: built {len(built)} files")
    if stale:
        print("Run: python examples/build.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
