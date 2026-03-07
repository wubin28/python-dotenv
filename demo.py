"""
demo.py - python-dotenv 功能演示脚本
运行前请确保：
  1. 已激活虚拟环境
  2. 已安装 python-dotenv：pip install -e ".[cli]"
  3. 已将 .env.example 复制为 .env：Copy-Item .env.example .env
"""

import os
from io import StringIO
from pathlib import Path

# ─────────────────────────────────────────────
# 演示 1：load_dotenv() —— 将 .env 注入 os.environ
# ─────────────────────────────────────────────
print("=" * 60)
print("演示 1：load_dotenv() —— 读取 .env 并写入 os.environ")
print("=" * 60)

from dotenv import load_dotenv

env_file = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_file)

print(f"APP_NAME    = {os.getenv('APP_NAME')}")
print(f"APP_ENV     = {os.getenv('APP_ENV')}")
print(f"APP_PORT    = {os.getenv('APP_PORT')}")
print(f"DOMAIN      = {os.getenv('DOMAIN')}")
print(f"ADMIN_EMAIL = {os.getenv('ADMIN_EMAIL')}")   # 变量引用展开
print(f"BASE_URL    = {os.getenv('BASE_URL')}")       # 变量引用展开
print(f"GREETING    = {os.getenv('GREETING')}")       # 引号已去除
print(f"DB_PASSWORD = {os.getenv('DB_PASSWORD')}")   # export 前缀已忽略
print(f"FULL_TITLE  = {os.getenv('FULL_TITLE')}")

# ─────────────────────────────────────────────
# 演示 2：dotenv_values() —— 返回 dict，不污染 os.environ
# ─────────────────────────────────────────────
print()
print("=" * 60)
print("演示 2：dotenv_values() —— 返回 dict，不修改 os.environ")
print("=" * 60)

from dotenv import dotenv_values

config = dotenv_values(env_file)
print("读取到的键值对：")
for key, value in config.items():
    print(f"  {key} = {value!r}")

# ─────────────────────────────────────────────
# 演示 3：override 开关行为对比
# ─────────────────────────────────────────────
print()
print("=" * 60)
print("演示 3：override=False（默认）vs override=True")
print("=" * 60)

# 先手动在 os.environ 中设置一个与 .env 相同的变量
os.environ["APP_ENV"] = "production"
print(f"手动设置 os.environ['APP_ENV'] = 'production'")

# override=False（默认）：不覆盖已有的环境变量
load_dotenv(dotenv_path=env_file, override=False)
print(f"override=False 后，APP_ENV = {os.getenv('APP_ENV')!r}  ← 保持 production")

# override=True：覆盖已有的环境变量
load_dotenv(dotenv_path=env_file, override=True)
print(f"override=True  后，APP_ENV = {os.getenv('APP_ENV')!r}  ← 改回 development")

# ─────────────────────────────────────────────
# 演示 4：从内存字符串流加载（stream 参数）
# ─────────────────────────────────────────────
print()
print("=" * 60)
print("演示 4：从 StringIO 流加载（无需文件）")
print("=" * 60)

stream_config = StringIO("SERVICE_URL=https://api.example.com\nTIMEOUT=30")
load_dotenv(stream=stream_config)
print(f"SERVICE_URL = {os.getenv('SERVICE_URL')}")
print(f"TIMEOUT     = {os.getenv('TIMEOUT')}")

print()
print("所有演示完成！")
