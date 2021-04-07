"""Automate release management."""
import argparse
import os
import subprocess

# Define release candidate branch name
RC_BRANCH_NAME = os.environ.get("RC_BRANCH_NAME", "next")
STABLE_BRANCH_NAME = os.environ.get("STABLE_BRANCH_NAME", "stable")

VERSION_CMD = "repo bump {version}"


def run(cmd: str) -> None:
    """Run a command using shell mode and check the return code."""
    p = subprocess.run(cmd, shell=True)
    p.check_returncode()


def prepare_release(version: str, branch: str) -> None:
    """Prepare the release."""
    run(f"git checkout {branch}")
    # Update version using command defined above
    run(VERSION_CMD.format(version=version))
    # At this point semantic release already performed a commit
    run("git add .")
    # Commit changes to the current branch
    run(
        f"git commit -m 'chore(release): bumped to version {version} [skip ci]' --no-verify"
    )


def publish_release(version: str, branch: str) -> None:
    """Perform the release."""
    # Generate name of new release branch
    if branch == "stable":
        release_branch = f"releases/stable/{version}"
    elif branch == RC_BRANCH_NAME:
        release_branch = f"releases/rc/{version}"
    else:
        raise ValueError(f"There is no rule to publish release for branch: {version}")
    # Push current branch to remote
    run(f"git push origin {branch}")
    # Checkout release branch
    run(f"git checkout -b {release_branch}")
    # Push release branch to remote
    run(f"git push origin {release_branch}")


def on_success(branch: str) -> None:
    """Merge changes back into next on success on stable releases only."""
    if branch == STABLE_BRANCH_NAME:
        # Checkout release candidate branch ("next" by default)
        run(f"git checkout {RC_BRANCH_NAME}")
        # Merge changes from release branch
        run(
            f"git merge --no-ff origin/{branch} -m 'chore: merge from stable branch [skip ci]'"
        )
        # Push changes into release candidate branch ("next" by default)
        run(f"git push origin {RC_BRANCH_NAME}")


cli_parser = argparse.ArgumentParser(description="Semantic release step runner")
cli_parser.add_argument("step", metavar="S", type=str)
cli_parser.add_argument("version", metavar="V", type=str)
cli_parser.add_argument("branch", metavar="V", type=str)


if __name__ == "__main__":
    # The script expect a single positional argument
    args = cli_parser.parse_args()
    # Parse arguments
    step: str = args.step
    version: str = args.version
    branch: str = args.branch
    # Execute function based on received "step" value:
    if step == "prepare":
        prepare_release(version, branch)
    if step == "publish":
        publish_release(version, branch)
    if step == "success":
        on_success(branch)
