import pytest
from pathlib import Path
from env_check import validate_env

VALID_ENV_CONTENT = (
    "DB_HOST=localhost\n"
    "DB_PORT=5432\n"
    "DB_NAME=analytics\n"
    "DB_USER=admin\n"
    "DB_PASSWORD=s3cret\n"
    "BATCH_SIZE=500\n"
    "MAX_RETRIES=3\n"
    "DRY_RUN=false\n"
)


# AC-H1: All vars valid → no errors, exit 0
def test_h1_all_valid(clean_env, tmp_path):
    (tmp_path / ".env").write_text(VALID_ENV_CONTENT, encoding="utf-8")
    errors = validate_env(dotenv_path=tmp_path / ".env")
    assert errors == []


# AC-H2: DRY_RUN accepts true/True/TRUE/1/false/False/0
@pytest.mark.parametrize("value", ["true", "True", "TRUE", "1", "false", "False", "0"])
def test_h2_dry_run_valid_values(clean_env, tmp_path, value):
    content = VALID_ENV_CONTENT.replace("DRY_RUN=false", f"DRY_RUN={value}")
    (tmp_path / ".env").write_text(content, encoding="utf-8")
    errors = validate_env(dotenv_path=tmp_path / ".env")
    assert errors == []


# AC-H3: DB_PORT boundary values 1 and 65535
@pytest.mark.parametrize("port", [1, 65535])
def test_h3_db_port_boundary(clean_env, tmp_path, port):
    content = VALID_ENV_CONTENT.replace("DB_PORT=5432", f"DB_PORT={port}")
    (tmp_path / ".env").write_text(content, encoding="utf-8")
    errors = validate_env(dotenv_path=tmp_path / ".env")
    assert errors == []


# AC-H4: MAX_RETRIES=0 → OK
def test_h4_max_retries_zero(clean_env, tmp_path):
    content = VALID_ENV_CONTENT.replace("MAX_RETRIES=3", "MAX_RETRIES=0")
    (tmp_path / ".env").write_text(content, encoding="utf-8")
    errors = validate_env(dotenv_path=tmp_path / ".env")
    assert errors == []


# AC-S1: .env file doesn't exist → 8 FAIL lines, exit 1
def test_s1_no_env_file(clean_env, tmp_path):
    errors = validate_env(dotenv_path=tmp_path / ".env")
    assert len(errors) == 8
    assert all(e.startswith("[FAIL]") for e in errors)


# AC-S2: DB_HOST missing
def test_s2_db_host_missing(clean_env, tmp_path):
    content = "\n".join(
        line for line in VALID_ENV_CONTENT.splitlines()
        if not line.startswith("DB_HOST=")
    ) + "\n"
    (tmp_path / ".env").write_text(content, encoding="utf-8")
    errors = validate_env(dotenv_path=tmp_path / ".env")
    assert "[FAIL] DB_HOST: 未设置" in errors


# AC-S3: DB_PASSWORD empty string
def test_s3_db_password_empty(clean_env, tmp_path):
    content = VALID_ENV_CONTENT.replace("DB_PASSWORD=s3cret", "DB_PASSWORD=")
    (tmp_path / ".env").write_text(content, encoding="utf-8")
    errors = validate_env(dotenv_path=tmp_path / ".env")
    assert "[FAIL] DB_PASSWORD: 值为空字符串" in errors


# AC-S4: DB_PORT non-integer
def test_s4_db_port_not_int(clean_env, tmp_path):
    content = VALID_ENV_CONTENT.replace("DB_PORT=5432", "DB_PORT=abc")
    (tmp_path / ".env").write_text(content, encoding="utf-8")
    errors = validate_env(dotenv_path=tmp_path / ".env")
    assert '[FAIL] DB_PORT: 无法转换为整数（当前值："abc"）' in errors


# AC-S5: DB_PORT out of range (0 and 65536)
@pytest.mark.parametrize("port,expected_val", [(0, 0), (65536, 65536)])
def test_s5_db_port_out_of_range(clean_env, tmp_path, port, expected_val):
    content = VALID_ENV_CONTENT.replace("DB_PORT=5432", f"DB_PORT={port}")
    (tmp_path / ".env").write_text(content, encoding="utf-8")
    errors = validate_env(dotenv_path=tmp_path / ".env")
    assert f"[FAIL] DB_PORT: 值超出范围（需满足 1 <= DB_PORT <= 65535，当前值：{expected_val}）" in errors


# AC-S6: BATCH_SIZE=0 and BATCH_SIZE=-1
@pytest.mark.parametrize("size", [0, -1])
def test_s6_batch_size_not_positive(clean_env, tmp_path, size):
    content = VALID_ENV_CONTENT.replace("BATCH_SIZE=500", f"BATCH_SIZE={size}")
    (tmp_path / ".env").write_text(content, encoding="utf-8")
    errors = validate_env(dotenv_path=tmp_path / ".env")
    assert "[FAIL] BATCH_SIZE: 值超出范围（需满足 BATCH_SIZE > 0）" in errors


# AC-S7: DRY_RUN=yes → invalid bool
def test_s7_dry_run_invalid(clean_env, tmp_path):
    content = VALID_ENV_CONTENT.replace("DRY_RUN=false", "DRY_RUN=yes")
    (tmp_path / ".env").write_text(content, encoding="utf-8")
    errors = validate_env(dotenv_path=tmp_path / ".env")
    assert '[FAIL] DRY_RUN: 非法布尔值（当前值："yes"，合法值为 true/false/1/0）' in errors


# AC-S8: Multiple errors in order
def test_s8_multiple_errors_in_order(clean_env, tmp_path):
    content = (
        "DB_HOST=localhost\n"
        "DB_PORT=abc\n"
        "DB_NAME=analytics\n"
        "DB_USER=admin\n"
        "DB_PASSWORD=\n"
        "BATCH_SIZE=-1\n"
        "MAX_RETRIES=3\n"
        "DRY_RUN=yes\n"
    )
    (tmp_path / ".env").write_text(content, encoding="utf-8")
    errors = validate_env(dotenv_path=tmp_path / ".env")
    assert len(errors) == 4
    assert '[FAIL] DB_PORT: 无法转换为整数（当前值："abc"）' == errors[0]
    assert "[FAIL] DB_PASSWORD: 值为空字符串" == errors[1]
    assert "[FAIL] BATCH_SIZE: 值超出范围（需满足 BATCH_SIZE > 0）" == errors[2]
    assert '[FAIL] DRY_RUN: 非法布尔值（当前值："yes"，合法值为 true/false/1/0）' == errors[3]

