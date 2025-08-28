from pathlib import Path
from code_runner import run_js, run_py
from code_runner.models import CodeRunResponse
from app_test.utils import logs_contain


def test_run_js():
    path = Path("app_test/code_scripts/test.js").resolve()
    result = run_js.execute_javascript(path=path)

    resp = CodeRunResponse.model_validate(result)
    assert resp.success is True
    assert resp.quiz_response is not None

    qr = resp.quiz_response
    # params / answers
    assert qr.params == {"a": 1, "b": 2}
    assert qr.correct_answers["sum"] == 3

    # value logs
    assert logs_contain(qr.logs, "This is the value of a", "1")
    assert logs_contain(qr.logs, "This is the value of b", "2")

    # structure log (JS): could be JSON stringified or object printed
    # we only require the prefix and presence of a/b inside the same line
    assert logs_contain(qr.logs, "Here is a structure")
    # and make sure a/b appear somewhere in that structure log
    assert logs_contain(qr.logs, "Here is a structure") and (
        logs_contain(qr.logs, "Here is a structure", '"a"', "1")  # JSON-ish
        or logs_contain(qr.logs, "Here is a structure", "a", "1")  # loose fallback
    )


def test_run_py():
    path = Path("app_test/code_scripts/test.py").resolve()
    result = run_py.run_generate_py(path=str(path))

    resp = CodeRunResponse.model_validate(result)
    assert resp.success is True
    assert resp.quiz_response is not None

    qr = resp.quiz_response
    # params / answers
    assert qr.params == {"a": 1, "b": 2}
    assert qr.correct_answers["sum"] == 3

    # value logs
    assert logs_contain(qr.logs, "This is the value of a", "1")
    assert logs_contain(qr.logs, "This is the value of b", "2")

    # structure log (Python repr): "This is a structure {'params': {'a': 1, 'b': 2}}"
    assert logs_contain(qr.logs, "This is a structure", "'params'")
    assert logs_contain(qr.logs, "This is a structure", "'a'", "1")
    assert logs_contain(qr.logs, "This is a structure", "'b'", "2")
