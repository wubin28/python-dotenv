import os
import sys
from dotenv import load_dotenv


VAR_SPECS = [
    {"name": "DB_HOST",     "type": "str"},
    {"name": "DB_PORT",     "type": "int",  "min": 1, "max": 65535},
    {"name": "DB_NAME",     "type": "str"},
    {"name": "DB_USER",     "type": "str"},
    {"name": "DB_PASSWORD", "type": "str"},
    {"name": "BATCH_SIZE",  "type": "int",  "min": 1, "range_desc": "BATCH_SIZE > 0"},
    {"name": "MAX_RETRIES", "type": "int",  "min": 0, "range_desc": "MAX_RETRIES >= 0"},
    {"name": "DRY_RUN",     "type": "bool"},
]

VALID_BOOLS = frozenset({"true", "false", "1", "0"})


def _check_int(name: str, value: str, spec: dict) -> str | None:
    try:
        int_val = int(value)
    except ValueError:
        return f'[FAIL] {name}: 无法转换为整数（当前值："{value}"）'

    lo, hi = spec.get("min"), spec.get("max")
    if hi is not None:
        if not (lo <= int_val <= hi):
            return f"[FAIL] {name}: 值超出范围（需满足 {lo} <= {name} <= {hi}，当前值：{int_val}）"
    elif lo is not None and int_val < lo:
        range_desc = spec.get("range_desc", f"{name} >= {lo}")
        return f"[FAIL] {name}: 值超出范围（需满足 {range_desc}）"
    return None


def collect_errors(env_vars: dict) -> list[str]:
    errors = []
    for spec in VAR_SPECS:
        name = spec["name"]
        value = env_vars.get(name)

        if value is None:
            errors.append(f"[FAIL] {name}: 未设置")
            continue

        if spec["type"] == "str":
            if value == "":
                errors.append(f"[FAIL] {name}: 值为空字符串")
        elif spec["type"] == "int":
            err = _check_int(name, value, spec)
            if err:
                errors.append(err)
        else:  # bool
            if value.lower() not in VALID_BOOLS:
                errors.append(f'[FAIL] {name}: 非法布尔值（当前值："{value}"，合法值为 true/false/1/0）')

    return errors


def validate_env(dotenv_path=None) -> list[str]:
    load_dotenv(dotenv_path=dotenv_path, override=True)
    return collect_errors(os.environ)


def main():
    errors = validate_env()
    if errors:
        for msg in errors:
            print(msg)
        sys.exit(1)
    else:
        print("[OK] 所有环境变量校验通过")
        sys.exit(0)


if __name__ == "__main__":
    main()
