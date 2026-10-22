import subprocess

import pytest


@pytest.fixture(autouse=True)
def prevent_live_keychain_reads(monkeypatch):
    original = subprocess.run

    def guarded_run(command, *args, **kwargs):
        if (
            isinstance(command, (list, tuple))
            and command
            and command[0] == "/usr/bin/security"
        ):
            raise AssertionError("Tests must mock macOS Keychain access")
        return original(command, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", guarded_run)
