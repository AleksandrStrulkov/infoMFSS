from __future__ import annotations

import subprocess
import sys


def run_command(command: list[str], step_name: str) -> None:
    print(f"\n[Quality Gate] >>> Запуск: {step_name}...")
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        print(f"\n[Quality Gate] ОШИБКА: Шаг '{step_name}' завершился с кодом {result.returncode}!")
        sys.exit(result.returncode)


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else "."

    run_command([sys.executable, "-m", "ruff", "check", target], "ruff check (линтинг и импорты)")
    run_command([sys.executable, "-m", "ruff", "format", "--check", target], "ruff format (стиль и отступы)")
    run_command([sys.executable, "-m", "basedpyright", target], "basedpyright (строгие типы)")

    pytest_target = target if target.startswith("tests") or "test" in target else "tests"
    run_command(
        [sys.executable, "-m", "pytest", pytest_target, "--cov=infoMFSS", "--cov-fail-under=70"],
        "pytest + coverage (тесты и покрытие)",
    )

    print("\n[Quality Gate] ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО (Exit code: 0)!")


if __name__ == "__main__":
    main()
