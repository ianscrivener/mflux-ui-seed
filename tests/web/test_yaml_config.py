"""Tests for mflux-web YAML settings: precedence, parsing, and coercion.

Precedence contract: command line > YAML > built-in defaults.
"""

import argparse
from pathlib import Path

import pytest

from mflux.web.seed.cli import build_parser, coerce_value, load_yaml, merge_settings

YAML_FULL = """\
host: 192.168.1.50
port: 8821
output_dir: ~/pictures/mflux
models_dir:
  - ~/AI/models
  - /opt/checkpoints
lora_dir:
  - ~/AI/loras
cache_size: 3
idle_unload: 0
max_upload_mb: 12
api_key: yaml-secret
api_key_file: ~/secrets/key.txt
require_auth: true
allowed_host:
  - mflux.tail1234.ts.net
tls_cert: ~/certs/mflux.pem
tls_key: ~/certs/mflux.key
behind_https: true
log_level: debug
"""


@pytest.fixture()
def yaml_file(tmp_path: Path) -> Path:
    path = tmp_path / "mflux-web.yaml"
    path.write_text(YAML_FULL)
    return path


def parse(argv: list[str]) -> argparse.Namespace:
    return build_parser().parse_args(argv)


class TestYamlParsing:
    def test_missing_file_returns_empty(self, tmp_path: Path) -> None:
        assert load_yaml(tmp_path / "nope.yaml") == {}
        assert load_yaml(None) == {}

    def test_comment_and_blank_lines_ignored(self, tmp_path: Path) -> None:
        path = tmp_path / "c.yaml"
        path.write_text("# comment\n\nhost: 0.0.0.0  # trailing\n")
        assert load_yaml(path) == {"host": "0.0.0.0"}

    def test_list_requires_open_key(self, tmp_path: Path) -> None:
        path = tmp_path / "bad.yaml"
        path.write_text("- orphan\n")
        with pytest.raises(SystemExit):
            load_yaml(path)

    def test_all_keys_parsed(self, yaml_file: Path) -> None:
        values = load_yaml(yaml_file)
        assert values["host"] == "192.168.1.50"
        assert values["models_dir"] == ["~/AI/models", "/opt/checkpoints"]
        assert values["behind_https"] == "true"


class TestPrecedence:
    def test_yaml_fills_unset_cli_options(self, yaml_file: Path) -> None:
        args = merge_settings(parse([]), load_yaml(yaml_file))
        assert args.host == "192.168.1.50"
        assert args.port == 8821
        assert args.output_dir == Path.home() / "pictures" / "mflux"
        assert args.models_dir == [Path.home() / "AI" / "models", Path("/opt/checkpoints")]
        assert args.cache_size == 3
        assert args.idle_unload == 0
        assert args.max_upload_mb == 12
        assert args.api_key == "yaml-secret"
        assert args.require_auth is True
        assert args.allowed_host == ["mflux.tail1234.ts.net"]
        assert args.behind_https is True
        assert args.log_level == "debug"

    def test_cli_overrides_yaml(self, yaml_file: Path) -> None:
        args = merge_settings(parse(["--host", "127.0.0.1", "--port", "9000"]), load_yaml(yaml_file))
        assert args.host == "127.0.0.1"
        assert args.port == 9000
        # untouched YAML values still apply
        assert args.cache_size == 3

    def test_defaults_without_yaml(self) -> None:
        args = merge_settings(parse([]), {})
        assert args.host == "127.0.0.1"
        assert args.port == 8001
        assert args.cache_size == 1
        assert args.idle_unload == 10
        assert args.require_auth is False
        assert args.models_dir == []
        assert args.log_level == "info"

    def test_scalar_list_options(self, tmp_path: Path) -> None:
        # A single value (no bullet list) still lands as a one-element list.
        path = tmp_path / "scalar.yaml"
        path.write_text("models_dir: ~/AI/models\n")
        args = merge_settings(parse([]), load_yaml(path))
        assert args.models_dir == [Path.home() / "AI" / "models"]


class TestCoercion:
    @pytest.mark.parametrize(
        ("raw", "flags", "expected"),
        [
            ("true", {"is_bool": True}, True),
            ("no", {"is_bool": True}, False),
            ("42", {"is_int": True}, 42),
            ("1.5", {"is_float": True}, 1.5),
            ("~/x", {"is_path": True}, Path.home() / "x"),
            (["a", "b"], {"is_list": True}, ["a", "b"]),
            ("single", {"is_list": True}, ["single"]),
            (["~/a", "~/b"], {"is_list": True, "is_path": True}, [Path.home() / "a", Path.home() / "b"]),
        ],
    )
    def test_coerce(self, raw, flags, expected) -> None:
        assert coerce_value(raw, **flags) == expected


class TestCliFlags:
    def test_booleans_accept_explicit_no(self) -> None:
        # --require-auth/--no-require-auth and --behind-https/--no-behind-https
        assert parse(["--no-require-auth"]).require_auth is False
        assert parse(["--require-auth"]).require_auth is True
        assert parse(["--behind-https"]).behind_https is True
        assert parse(["--no-behind-https"]).behind_https is False
