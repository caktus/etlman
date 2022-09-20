import os
import subprocess
import tempfile


class SubprocessBackend:
    RUN_ARGS = {
        ("windows", "python"): ["Python.exe"],
        ("windows", "r"): ["Rscript.exe"],
        ("posix", "python"): ["/usr/bin/env", "python"],
        ("posix", "r"): ["/usr/bin/env", "Rscript"],
    }

    def _get_run_args(self, language: str):
        try:
            return self.RUN_ARGS[(os.name, language)]
        except KeyError:
            raise ValueError(f"Language {language} on {os.name} OS is not supported.")

    def execute_script(self, language: str, script: str) -> tuple[int, str, str]:
        run_args = self._get_run_args(language)
        with tempfile.NamedTemporaryFile() as f:
            f.write(script.encode("utf-8"))
            f.flush()
            result = subprocess.run([*run_args, f.name], capture_output=True)
        return (
            result.returncode,
            result.stdout.decode("utf-8"),
            result.stderr.decode("utf-8"),
        )
