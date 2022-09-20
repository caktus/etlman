import subprocess

import pytest

from etlman.backends.subprocess_backend import SubprocessBackend


class TestPythonSubprocessBackend:
    LANGUAGE = "python"
    STDOUT_TEST = "out to stdout"
    STDERR_TEST = "out to stderr"
    TEST_SCRIPT = f"""
import sys
print("{STDERR_TEST}", file=sys.stderr)
print("{STDOUT_TEST}", file=sys.stdout)
sys.exit({{exitcode}})
"""

    def test_success(self):
        backend = SubprocessBackend()
        exitcode, stdout, stderr = backend.execute_script(
            self.LANGUAGE, self.TEST_SCRIPT.format(exitcode=0)
        )
        assert stderr.strip() == self.STDERR_TEST
        assert stdout.strip() == self.STDOUT_TEST
        assert exitcode == 0

    def test_failure(self):
        backend = SubprocessBackend()
        exitcode, stdout, stderr = backend.execute_script(
            self.LANGUAGE, self.TEST_SCRIPT.format(exitcode=1)
        )
        assert stderr.strip() == self.STDERR_TEST
        assert stdout.strip() == self.STDOUT_TEST
        assert exitcode == 1


@pytest.mark.skipif(
    subprocess.run(["which", "Rscript"]).returncode != 0,
    reason="requires Rscript to be installed",
)
class TestRScriptSubprocessBackend:
    LANGUAGE = "r"
    STDOUT_TEST = "out to stdout"
    STDERR_TEST = "out to stderr"
    TEST_SCRIPT = f"""
write("{STDERR_TEST}", stderr())
write("{STDOUT_TEST}", stdout())
quit(status={{exitcode}})
"""

    def test_success(self):
        backend = SubprocessBackend()
        exitcode, stdout, stderr = backend.execute_script(
            self.LANGUAGE, self.TEST_SCRIPT.format(exitcode=0)
        )
        assert stderr.strip() == self.STDERR_TEST
        assert stdout.strip() == self.STDOUT_TEST
        assert exitcode == 0

    def test_failure(self):
        backend = SubprocessBackend()
        exitcode, stdout, stderr = backend.execute_script(
            self.LANGUAGE, self.TEST_SCRIPT.format(exitcode=1)
        )
        assert stderr.strip() == self.STDERR_TEST
        assert stdout.strip() == self.STDOUT_TEST
        assert exitcode == 1
