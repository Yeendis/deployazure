import os
import stat
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "create-vm-windowsrv.sh"


def _create_fake_az(tmp_path: Path) -> Path:
    """
    Cria um executável fake chamado 'az' que grava todas as chamadas
    em um arquivo de log para o teste validar depois.
    """
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    log_file = tmp_path / "az_calls.log"
    fake_az = fake_bin / "az"

    fake_az.write_text(
        f"""#!/bin/bash
set -e

echo "$@" >> "{log_file}"

# simula respostas de sucesso dos comandos
if [ "$1" = "group" ] && [ "$2" = "create" ]; then
  echo '{{"name":"rg-vm02","location":"eastus"}}'
  exit 0
fi

if [ "$1" = "vm" ] && [ "$2" = "create" ]; then
  echo '{{"powerState":"VM running"}}'
  exit 0
fi

if [ "$1" = "vm" ] && [ "$2" = "open-port" ]; then
  echo '{{"port":3389}}'
  exit 0
fi

exit 0
""",
        encoding="utf-8",
    )

    fake_az.chmod(fake_az.stat().st_mode | stat.S_IEXEC)
    return log_file


def test_script_fails_without_admin_password(tmp_path):
    env = os.environ.copy()
    env.pop("ADMIN_PASSWORD", None)

    result = subprocess.run(
        ["bash", str(SCRIPT_PATH)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "ADMIN_PASSWORD" in (result.stdout + result.stderr)


def test_script_executes_expected_azure_commands(tmp_path):
    log_file = _create_fake_az(tmp_path)

    env = os.environ.copy()
    env["ADMIN_PASSWORD"] = "SenhaForte@123"
    env["PATH"] = f"{tmp_path / 'bin'}{os.pathsep}{env['PATH']}"

    result = subprocess.run(
        ["bash", str(SCRIPT_PATH)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    calls = log_file.read_text(encoding="utf-8").strip().splitlines()

    assert len(calls) == 3

    assert calls[0] == "group create --name rg-vm02 --location eastus"

    assert "vm create" in calls[1]
    assert "--resource-group rg-vm02" in calls[1]
    assert "--name vm-srv01" in calls[1]
    assert "--image Win2022Datacenter" in calls[1]
    assert "--size Standard_B2s" in calls[1]
    assert "--admin-username adminuser" in calls[1]
    assert "--admin-password SenhaForte@123" in calls[1]
    assert "--authentication-type password" in calls[1]

    assert calls[2] == "vm open-port --port 3389 --resource-group rg-vm02 --name vm-srv01"
