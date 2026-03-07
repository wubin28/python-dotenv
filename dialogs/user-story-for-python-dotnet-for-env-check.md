# User Story：应用启动前环境变量校验工具（env-check）

---

## User Story

**作为**一名在本地开发环境中维护数据导入脚本的数据工程师，
**我想**在运行 `import_data.py` 之前执行 `env_check.py` 对 `.env` 文件中的所有必需配置项进行校验，
**以便**在任何数据被写入数据库之前就发现配置错误，避免因配置缺失或格式错误导致脚本在执行中途崩溃。

---

## 背景与约束

- `env_check.py` 使用 `python-dotenv` 的 `load_dotenv()` 将 `.env` 文件加载进 `os.environ`
- 校验基于以下硬编码的"必需变量清单"：

| 变量名 | 期望类型 | 取值约束 |
|---|---|---|
| `DB_HOST` | `str` | 非空 |
| `DB_PORT` | `int` | `1 <= DB_PORT <= 65535` |
| `DB_NAME` | `str` | 非空 |
| `DB_USER` | `str` | 非空 |
| `DB_PASSWORD` | `str` | 非空 |
| `BATCH_SIZE` | `int` | `BATCH_SIZE > 0` |
| `MAX_RETRIES` | `int` | `MAX_RETRIES >= 0` |
| `DRY_RUN` | `bool` | 只接受 `"true"` / `"false"` / `"1"` / `"0"`（大小写不敏感） |

- 所有错误必须**一次性全部输出**，不能遇到第一个错误就停止
- 校验通过：打印 `[OK] 所有环境变量校验通过`，进程以退出码 `0` 退出
- 校验失败：打印每条 `[FAIL] <变量名>: <原因>`，最后进程以退出码 `1` 退出

---

## Acceptance Criteria

### Happy Path

---

**AC-H1：所有必需变量均已正确配置**

```
Given .env 文件存在，且包含以下内容：
      DB_HOST=localhost
      DB_PORT=5432
      DB_NAME=analytics
      DB_USER=admin
      DB_PASSWORD=s3cret
      BATCH_SIZE=500
      MAX_RETRIES=3
      DRY_RUN=false

When  用户运行 python env_check.py

Then  终端输出：[OK] 所有环境变量校验通过
And   进程退出码为 0
```

---

**AC-H2：DRY_RUN 接受所有合法布尔字符串（大小写不敏感）**

```
Given .env 文件中其他变量均合法，且分别测试以下 DRY_RUN 值：
      DRY_RUN=true
      DRY_RUN=True
      DRY_RUN=TRUE
      DRY_RUN=1
      DRY_RUN=false
      DRY_RUN=False
      DRY_RUN=0

When  用户运行 python env_check.py

Then  每种情况下终端均输出：[OK] 所有环境变量校验通过
And   每种情况下进程退出码均为 0
```

---

**AC-H3：DB_PORT 接受合法端口号边界值**

```
Given .env 文件中其他变量均合法，且分别测试：
      DB_PORT=1
      DB_PORT=65535

When  用户运行 python env_check.py

Then  两种情况下终端均输出：[OK] 所有环境变量校验通过
And   进程退出码均为 0
```

---

**AC-H4：MAX_RETRIES 接受 0（允许不重试）**

```
Given .env 文件中其他变量均合法，且 MAX_RETRIES=0

When  用户运行 python env_check.py

Then  终端输出：[OK] 所有环境变量校验通过
And   进程退出码为 0
```

---

### Sad Path

---

**AC-S1：.env 文件不存在**

```
Given 当前目录下没有 .env 文件

When  用户运行 python env_check.py

Then  终端为每个必需变量各输出一条 [FAIL] 行，例如：
      [FAIL] DB_HOST: 未设置
      [FAIL] DB_PORT: 未设置
      ...（共 8 条）
And   进程退出码为 1
```

---

**AC-S2：必需变量完全缺失（.env 文件存在但未包含该变量）**

```
Given .env 文件存在，但其中没有 DB_HOST 这一行（key 完全不存在）

When  用户运行 python env_check.py

Then  终端输出包含：[FAIL] DB_HOST: 未设置
And   进程退出码为 1
```

---

**AC-S3：必需变量值为空字符串（key 存在但值为空）**

```
Given .env 文件存在，且包含：DB_PASSWORD=
      （key 存在，但等号右侧为空，即空字符串）

When  用户运行 python env_check.py

Then  终端输出包含：[FAIL] DB_PASSWORD: 值为空字符串
And   进程退出码为 1

Note  此处是关键 bug 场景：
      错误实现 `if not os.getenv('DB_PASSWORD')` 会将空字符串误判为"未设置"，
      但正确实现应区分"key 不存在（None）"与"key 存在但值为空（''）"两种情况，
      并对空字符串给出明确的"值为空字符串"错误提示，而非"未设置"。
```

---

**AC-S4：int 类型变量值无法转换为整数**

```
Given .env 文件存在，且包含：DB_PORT=abc

When  用户运行 python env_check.py

Then  终端输出包含：[FAIL] DB_PORT: 无法转换为整数（当前值："abc"）
And   进程退出码为 1
And   程序不抛出未捕获的 ValueError 异常（不崩溃）
```

---

**AC-S5：int 类型变量值超出允许范围（DB_PORT 越界）**

```
Given .env 文件存在，且分别测试：
      DB_PORT=0
      DB_PORT=65536

When  用户运行 python env_check.py

Then  两种情况下终端均输出包含：
      [FAIL] DB_PORT: 值超出范围（需满足 1 <= DB_PORT <= 65535，当前值：0）
      [FAIL] DB_PORT: 值超出范围（需满足 1 <= DB_PORT <= 65535，当前值：65536）
And   进程退出码均为 1
```

---

**AC-S6：int 类型变量值超出允许范围（BATCH_SIZE 非正数）**

```
Given .env 文件存在，且包含：BATCH_SIZE=0
      或 BATCH_SIZE=-1

When  用户运行 python env_check.py

Then  终端输出包含：[FAIL] BATCH_SIZE: 值超出范围（需满足 BATCH_SIZE > 0）
And   进程退出码为 1
```

---

**AC-S7：DRY_RUN 值不是合法布尔字符串**

```
Given .env 文件存在，且包含：DRY_RUN=yes

When  用户运行 python env_check.py

Then  终端输出包含：
      [FAIL] DRY_RUN: 非法布尔值（当前值："yes"，合法值为 true/false/1/0）
And   进程退出码为 1

Note  此处是关键 bug 场景：
      错误实现 `if os.getenv('DRY_RUN') == False` 会导致条件永远不成立，
      因为 os.getenv 始终返回字符串，字符串永远不等于布尔值 False。
```

---

**AC-S8：多个变量同时校验失败时，所有错误一次性全部输出**

```
Given .env 文件存在，且包含以下错误：
      DB_PORT=abc           （无法转换为整数）
      BATCH_SIZE=-1         （超出范围）
      DRY_RUN=yes           （非法布尔值）
      DB_PASSWORD=          （空字符串）

When  用户运行 python env_check.py

Then  终端输出 4 条 [FAIL] 行（每个错误变量各一条），顺序与清单定义顺序一致
And   不因第一个错误就提前终止输出
And   进程退出码为 1
```

---

## 术语说明

| 术语 | 含义 |
|---|---|
| "未设置" | `.env` 中该 key 完全不存在，`os.getenv()` 返回 `None` |
| "值为空字符串" | `.env` 中该 key 存在但等号右侧为空，`os.getenv()` 返回 `""` |
| 退出码 0 | 校验全部通过，`import_data.py` 可以安全启动 |
| 退出码 1 | 至少一项校验失败，`import_data.py` 不应启动 |
