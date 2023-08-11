import gzip
import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock

import requests
from typer.testing import CliRunner

from canonical_package_statistics.app import Arch, app, main, parse_file_rows, persist_file, read_gzip_file


def test_read_gzip_file():
    lines_ = [b"this is some test data\n", b"with 2 lines"]
    data = b"".join(lines_)
    g_zip_data = gzip.compress(data)
    file_like_data = BytesIO(g_zip_data)
    res = read_gzip_file(file_like_data)
    assert res == lines_


def test_persist_file():
    tmp_file = tempfile.NamedTemporaryFile()
    tmp_file_path = Path(tmp_file.name)
    data = b"test data"
    persist_file(tmp_file_path, data)
    with open(tmp_file_path, "rb") as f:
        read_data = f.read()
    assert read_data == data


TEST_DATA = b"""
usr/lib/python3/dist-packages/kajiki-0.9.2.egg-info/requires.txt python/python3-kajiki
usr/lib/python3/dist-packages/kajiki/__init__.py        python/python3-kajiki
usr/lib/python3/dist-packages/kajiki/__main__.py        python/python3-kajiki
usr/lib/python3/dist-packages/kajiki/doctype.py         python/python3-kajiki
usr/lib/python3/dist-packages/kajiki/html_utils.py      python/python3-kajiki
usr/lib/python3/dist-packages/kajiki/i18n.py            python/python3-kajiki
var/lib/wims/public_html/modules/help/example/oefquicktool.fr/src/practice_pasts_case.oef web/wims-help
var/lib/wims/public_html/modules/help/example/oefquicktool.fr/src/voca_histoire.oef web/wims-help
var/lib/wims/public_html/modules/help/example/oefquicktool.fr/src/word_stress_patterns_tonic.oef web/wims-help
usr/lib/python3/dist-packages/mailman/templates/he/list:user:notice:warning.txt mail/mailman3
usr/lib/python3/dist-packages/mailman/templates/he/list:user:notice:welcome.txt mail/mailman3
usr/lib/python3/dist-packages/mailman/templates/hu/list:admin:notice:disable.txt mail/mailman3
usr/lib/python3/dist-packages/mailman/templates/hu/list:admin:notice:removal.txt mail/mailman3
    """.strip()


def test_parse_file_rows():
    counts = parse_file_rows(TEST_DATA.split(b"\n"))
    print(counts)
    assert {b"python/python3-kajiki": 6, b"mail/mailman3": 4, b"web/wims-help": 3}


runner = CliRunner()


def test_main(monkeypatch, capsys):
    mock_res = MagicMock()
    mock_res.content = gzip.compress(TEST_DATA)

    def mock_get(*args, **kwargs):
        return mock_res

    monkeypatch.setattr(requests, "get", mock_get)

    cachedir = tempfile.gettempdir()
    main(Arch.amd64, cache=True, cache_dir=Path(cachedir))

    captured = capsys.readouterr()
    assert "1. python/python3-kajiki 6" in captured.out
    assert "2. mail/mailman3 4" in captured.out
    assert "3. web/wims-help" in captured.out


def test_main_fail_arch():
    result = runner.invoke(app, ["totally-armhf"])
    assert result.exit_code == 2
