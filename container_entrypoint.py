#!/usr/bin/env python3
"""Initialize writable directories and run N31L without root privileges."""

import os
import re
import sys
from collections.abc import Callable
from typing import NoReturn, cast

MAX_LINUX_ID = 2**32 - 2
WRITABLE_DIRECTORIES = ("/data", "/run/n31l")
CHOWN = cast(Callable[..., None], getattr(os, "chown"))
GETEGID = cast(Callable[[], int], getattr(os, "getegid"))
GETEUID = cast(Callable[[], int], getattr(os, "geteuid"))
SETGID = cast(Callable[[int], None], getattr(os, "setgid"))
SETGROUPS = cast(Callable[[list[int]], None], getattr(os, "setgroups"))
SETUID = cast(Callable[[int], None], getattr(os, "setuid"))


def fail(message: str) -> NoReturn:
    """Exit with a container initialization error."""
    print(f"container-entrypoint: error: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_linux_id(name: str) -> int:
    """Read and validate a positive numeric Linux user or group ID."""
    value = os.environ.get(name)
    if value is None:
        fail(f"{name} is not set")
    if not re.fullmatch(r"[0-9]+", value):
        fail(f"{name} must be a positive numeric Linux ID, got {value!r}")

    identifier = int(value)
    if identifier == 0:
        fail(f"{name} must be greater than zero")
    if identifier > MAX_LINUX_ID:
        fail(f"{name} must not exceed {MAX_LINUX_ID}")
    return identifier


def chown_tree(path: str, uid: int, gid: int) -> None:
    """Create and recursively assign a writable directory without following links."""
    os.makedirs(path, mode=0o755, exist_ok=True)
    if os.path.islink(path):
        fail(f"writable directory {path} must not be a symbolic link")

    CHOWN(path, uid, gid, follow_symlinks=False)
    for directory, subdirectories, filenames in os.walk(path, followlinks=False):
        for name in (*subdirectories, *filenames):
            item = os.path.join(directory, name)
            if not os.path.islink(item):
                CHOWN(item, uid, gid, follow_symlinks=False)


def main() -> NoReturn:
    """Initialize the container and replace it with the requested process."""
    uid = read_linux_id("PUID")
    gid = read_linux_id("PGID")

    if GETEUID() != 0:
        print(
            f"container-entrypoint: running as Docker UID {GETEUID()}:GID {GETEGID()}; "
            f"PUID={uid} and PGID={gid} were not applied because initialization requires root",
            file=sys.stderr,
        )
    else:
        for path in WRITABLE_DIRECTORIES:
            chown_tree(path, uid, gid)

        SETGROUPS([])
        SETGID(gid)
        SETUID(uid)

    if len(sys.argv) == 1:
        fail("no application command was provided")
    os.execvp(sys.argv[1], sys.argv[1:])


if __name__ == "__main__":
    main()
