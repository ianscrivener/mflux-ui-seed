"""Namespace regression tests for the mflux.web.seed child distribution.

Adapted from tests/test_namespace_extensions.py in mflux-community/mflux
(PR #776), which defines the implicit mflux.web namespace contract this
distribution follows: never ship mflux/__init__.py or mflux/web/__init__.py;
each UI owns a unique child directory only.
"""

import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"


class TestNamespaceContract:
    def test_no_parent_initializers_shipped(self) -> None:
        # The mflux PR #776 contract: a child distribution must never ship
        # mflux/__init__.py (owned by core) or mflux/web/__init__.py
        # (mflux.web must stay an implicit namespace package).
        assert not (SRC / "mflux" / "__init__.py").exists()
        assert not (SRC / "mflux" / "web" / "__init__.py").exists()
        # This distribution's child owns exactly one directory.
        assert (SRC / "mflux" / "web" / "seed").is_dir()


class TestChildImport:
    def test_import_without_core_in_subprocess(self) -> None:
        # No core required: with only this distribution's src on sys.path,
        # the child imports through pure implicit namespace mechanics.
        code = (
            f"import sys; sys.path[:0] = {[str(SRC)]!r}\n"
            "import mflux, mflux.web\n"
            "from mflux.web.seed import settings\n"
            "assert settings.DEFAULT_HOST\n"
            "assert mflux.web.__file__ is None\n"
        )
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-c", code],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout == ""

    def test_two_ui_distributions_merge(self, tmp_path: Path) -> None:
        # Two independent child distributions in separate directories merge
        # into the shared implicit mflux.web namespace (PR #776 model).
        other_root = tmp_path / "other_distribution"
        other = other_root / "mflux" / "web" / "other_ui"
        other.mkdir(parents=True)
        (other / "__init__.py").write_text("VALUE = 7\n", encoding="utf-8")
        code = (
            f"import sys; sys.path[:0] = {[str(SRC), str(other_root)]!r}\n"
            "import mflux.web.other_ui\n"
            "from mflux.web.seed import settings\n"
            "assert mflux.web.other_ui.VALUE == 7\n"
            "assert settings.DEFAULT_HOST\n"
            "assert mflux.web.__file__ is None\n"
        )
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-c", code],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
