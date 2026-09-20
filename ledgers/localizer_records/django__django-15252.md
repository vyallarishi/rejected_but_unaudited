# Instance: `django__django-15252`

- runs: 1   termination: `ledger_informed`   think-high calls: 2

## Issue (truncated to 1200 chars)

```
MigrationRecorder does not obey db_router allow_migrate rules
Description
	
Hi,
We have a multi-db setup. We have one connection that is for the django project, and several connections that talk to other dbs for information (ie models with managed = False). Django should only create tables in the first connection, never in any of the other connections. We have a simple router that does the following: 
class Router(object):
	def allow_migrate(self, db, model):
		if db == 'default':
			return True
		return False
Current Behaviour
We run our functional tests and the migrate command is called against each connection when the test databases are created (see django/test/runner.py, setup_databases, line 300-ish, which calls django/db/backends/creation.py, create_test_db, line 377-ish)
When this migrate runs, it tries to apply our migrations, which tries to record that a migration has been applied (see django/db/migrations/executor.py, apply_migration, which has several calls to self.recorder.record_applied). 
The first thing that record_applied does is a call to self.ensure_schema() (see django/db/migrations/recorder.py, record_applied, lien 66-ish). 
ensure_schema checks to see if the Mi
```

## Stage 3 — Symptoms extracted

- exception types: `[]`
- error messages: `[]`
- behaviors: `['table creation', 'migration recording', 'schema checking']`
- named APIs: `['MigrationRecorder.record_applied', 'MigrationRecorder.ensure_schema']`
- stack frames: `[{'file': 'django/test/runner.py', 'func': 'setup_databases', 'line': 300}, {'file': 'django/db/backends/creation.py', 'func': 'create_test_db', 'line': 377}, {'file': 'django/db/migrations/recorder.py', 'func': 'record_applied', 'line': 66}]`

## Stage 1 — LLM file ranking (top 10)

| # | file | reason |
|---|------|--------|
| 1 | `django/db/migrations/recorder.py` | The issue is about MigrationRecorder not obeying db_router rules, so this file is central to the problem. |
| 2 | `django/db/backends/base/base.py` | This file likely contains the base connection handling logic that needs to respect db_router rules. |
| 3 | `django/db/router.py` | This file implements the database router, which is the core component that should be respected by MigrationRecorder. |
| 4 | `django/db/backends/__init__.py` | This file is the entry point for database backends and might be involved in connection setup. |
| 5 | `django/db/migrations/executor.py` | This file is responsible for applying migrations and calls MigrationRecorder. |
| 6 | `django/db/backends/base/creation.py` | This file contains the logic for creating test databases, which is where the issue is triggered. |
| 7 | `django/db/migrations/loader.py` | This file loads migration files and their status, which is relevant to the issue. |
| 8 | `django/db/backends/sqlite3/base.py` | The issue occurs during test database creation, so the SQLite backend might need edits. |
| 9 | `django/db/backends/postgresql/base.py` | The issue occurs during test database creation, so the Postgres backend might need edits. |
| 10 | `django/db/backends/mysql/base.py` | The issue occurs during test database creation, so the MySQL backend might need edits. |

## Stage 4 — Hypothesis ledger evolution

### Abductive step #1 (iteration=3)

- leading: 1, considering: 1, rejected: 1

**Per-candidate deliberation traces**

#### ✓ LEADING — `django/db/migrations/recorder.py::MigrationRecorder.ensure_schema`

- **Q1 Role.** This function ensures that the `django_migrations` table exists in the database, creating it if it's missing.
- **Q2 Connection to symptom.** Yes, this function directly produces the symptom. When `record_applied` is called for a database connection that does not have the `django_migrations` table, this function is invoked. It checks if the table exists with `self.has_table()`, which returns false. It then proceeds to call `editor.create_model(self.Migration)` without first checking if migrations are allowed on the current database via the database router (`allow_migrate`). This unconditional creation is the reported incorrect behavior.
- **Q3 Counterfactual.** `yes` — If this function were modified to first consult the database router using `allow_migrate` and only proceed if allowed, the `django_migrations` table would not be created on disallowed databases, eliminating the symptom.
- **Q4 Alternatives considered.**
  - `django/db/migrations/recorder.py::MigrationRecorder.record_applied` — The check could be in the caller, but fixing it here is more robust as `ensure_schema` is called by other methods too.
  - `django/db/backends/base/schema.py::BaseSchemaEditor.create_model` — This is too low-level; the decision logic for whether to migrate belongs at a higher level than the schema editor itself.
  - `django/test/runner.py::setup_databases` — Fixing it in the test runner would be too specific and wouldn't solve the problem for the general `migrate` command.
- **Q5 Verdict.** `leading` (confidence: `high`) — This function unconditionally creates the migrations table without consulting the database router, which is the direct cause of the symptom.

#### … CONSIDERING — `django/db/migrations/recorder.py::MigrationRecorder.record_applied`

- **Q1 Role.** This function records that a specific migration has been successfully applied by creating a new row in the `django_migrations` table.
- **Q2 Connection to symptom.** Yes, this function contributes to the symptom by being a direct caller of `ensure_schema`. The execution path described in the issue report flows through `record_applied`, which calls `self.ensure_schema()` unconditionally at the beginning of its execution, thereby triggering the incorrect table creation.
- **Q3 Counterfactual.** `partially` — Adding a router check here before calling `ensure_schema` would fix this specific call path. However, other methods like `applied_migrations` also call `ensure_schema`, so the fix would be incomplete.
- **Q4 Alternatives considered.**
  - `django/db/migrations/recorder.py::MigrationRecorder.ensure_schema` — This is the preferred location for the fix, as it would cover all call sites and place the check closest to the action.
  - `django/db/migrations/executor.py::MigrationExecutor.apply_migration` — The check could be placed further up the stack, but the `MigrationRecorder` should arguably be responsible for its own model's routing.
- **Q5 Verdict.** `considering` (confidence: `high`) — This function calls the problematic `ensure_schema` without any guards, but fixing it here is less robust than fixing `ensure_schema` itself.

#### ✗ REJECTED — `django/db/utils.py::ConnectionRouter.allow_migrate`

- **Q1 Role.** This function consults all configured database routers to determine if a migration for a given app label is allowed on a specific database connection.
- **Q2 Connection to symptom.** No path exists. The symptom is caused by the *absence* of a call to this function from `MigrationRecorder.ensure_schema`. The function itself behaves correctly, but it is never invoked during the problematic table creation process.
- **Q3 Counterfactual.** `no` — Modifying this function would have no effect on the symptom, as it is not being called by the code path that creates the `django_migrations` table.
- **Q4 Alternatives considered.**
  - `django/db/migrations/recorder.py::MigrationRecorder.ensure_schema` — This is the function that should be calling `allow_migrate`.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is not called and therefore cannot be the source of the bug; its absence in the call stack is the problem.

**✓ Leading**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/migrations/recorder.py::MigrationRecorder.ensure_schema` | high | This function unconditionally creates the migrations table without consulting the database router, which is the direct cause of the symptom. | Before creating the table, check `router.allow_migrate(self.connection.alias, self.Migration._meta.app_label)` and return if it's `False`. |

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/migrations/recorder.py::MigrationRecorder.record_applied` | high | This function calls the problematic `ensure_schema` without any guards, but fixing it here is less robust than fixing `ensure_schema` itself. | Add a guard using `router.allow_migrate` at the beginning of the function to prevent calls to `ensure_schema` on disallowed databases. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/utils.py::ConnectionRouter.allow_migrate` | high | This function is not called and therefore cannot be the source of the bug; its absence in the call stack is the problem. |  |

**Causal chains (per candidate)**

- `django/db/migrations/recorder.py::MigrationRecorder.ensure_schema`  (score=10.0)  \
  The test runner calls `migrate` on a non-`default` database. → `MigrationExecutor` calls `recorder.record_applied`. → `record_applied` calls `self.ensure_schema()`. → Inside `ensure_schema`, `self.has_table()` returns `False`. → The code proceeds to `editor.create_model(self.Migration)` without checking `router.allow_migrate`. → The `django_migrations` table is created on a database where it should be disallowed, causing the symptom.
- `django/db/migrations/recorder.py::MigrationRecorder.record_applied`  (score=7.0)  \
  The migration executor calls `record_applied` for a migration on a non-`default` database. → The first line of `record_applied` is `self.ensure_schema()`. → This call triggers the problematic behavior in `ensure_schema`, which creates the `django_migrations` table without checking router rules.
- `django/db/utils.py::ConnectionRouter.allow_migrate`  (score=0.0)  \
  This function is not part of the execution path that leads to the symptom.

**next_to_explore:** `['django/db/migrations/recorder.py::MigrationRecorder.applied_migrations', 'django/db/migrations/recorder.py::MigrationRecorder.has_table', 'django/db/migrations/executor.py::MigrationExecutor.apply_migration', 'django/db/backends/base/schema.py::BaseSchemaEditor.create_model']`

### Abductive step #2 (iteration=6)

- leading: 0, considering: 2, rejected: 1

**Per-candidate deliberation traces**

#### … CONSIDERING — `django/db/migrations/recorder.py::MigrationRecorder.has_table`

- **Q1 Role.** This function checks if the `django_migrations` table exists in the current database connection.
- **Q2 Connection to symptom.** Yes, this function is part of the causal path. `MigrationRecorder.ensure_schema` calls `self.has_table()` to determine if the migrations table exists. When `has_table()` returns `False` for a non-default database, `ensure_schema` proceeds to try and create the table, which is the symptomatic behavior. The function itself is correct, but its return value is used by its caller to make an incorrect decision.
- **Q3 Counterfactual.** `no` — Modifying this function would not fix the root cause. The decision to create the table is made in the calling function, `ensure_schema`, which should be checking the `allow_migrate` router rule.
- **Q4 Alternatives considered.**
  - `recorder.py::MigrationRecorder.ensure_schema` — Preferred, as it's the function that decides to create the table and should be responsible for checking permissions.
  - `executor.py::MigrationExecutor.apply_migration` — Less preferred; this is upstream and fixing it here would be a patch, not a fix for the recorder's incorrect assumption.
- **Q5 Verdict.** `considering` (confidence: `high`) — This function is a key part of the causal chain by reporting the table's absence, but the fault lies with its caller, `ensure_schema`.

#### ✗ REJECTED — `django/db/migrations/recorder.py::MigrationRecorder.applied_migrations`

- **Q1 Role.** This function returns a dictionary of all applied migrations by querying the `django_migrations` table.
- **Q2 Connection to symptom.** No path. This function checks for the table's existence using `has_table()`. If the table does not exist, it correctly returns an empty dictionary, indicating no migrations have been applied. It does not attempt to create the table, and therefore does not produce the symptom.
- **Q3 Counterfactual.** `no` — This function does not cause the symptom of unwanted table creation, so modifying it would have no effect on the issue.
- **Q4 Alternatives considered.**
  - `recorder.py::MigrationRecorder.ensure_schema` — This is the function that actually attempts to create the table, unlike `applied_migrations`.
  - `recorder.py::MigrationRecorder.record_applied` — This is the public API method that leads to the problematic `ensure_schema` call.
- **Q5 Verdict.** `rejected` (confidence: `high`) — This function is not on the causal path to the symptom; its handling of a missing table is correct and does not trigger table creation.

#### … CONSIDERING — `django/db/migrations/executor.py::MigrationExecutor.apply_migration`

- **Q1 Role.** This function orchestrates the application of a single migration, running its database operations and then recording its application.
- **Q2 Connection to symptom.** Yes, this function is an upstream cause. After applying a migration's schema changes, it calls `self.record_migration(migration)`, which in turn calls `self.recorder.record_applied(...)`. This call is made for every database connection the migration command is run against, regardless of the `allow_migrate` router rule, thereby initiating the sequence that leads to the unwanted table creation.
- **Q3 Counterfactual.** `partially` — Adding a check for `allow_migrate` before calling `self.record_migration` would prevent the symptom. However, the root issue is that the `MigrationRecorder` itself is not router-aware, so the fix is better placed there.
- **Q4 Alternatives considered.**
  - `recorder.py::MigrationRecorder.ensure_schema` — Preferred. The component performing the action (creating a table) should be responsible for checking permissions.
  - `test/runner.py::setup_databases` — Not preferred. Fixing the issue this far upstream would be a workaround for a fundamental flaw in the migration framework.
- **Q5 Verdict.** `considering` (confidence: `medium`) — This function triggers the problematic behavior, but the core logic error of ignoring the DB router is in the downstream `MigrationRecorder`.

**… Considering**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/migrations/recorder.py::MigrationRecorder.has_table` | high | This function is a key part of the causal chain by reporting the table's absence, but the fault lies with its caller, `ensure_schema`. | The caller, `ensure_schema`, should check `allow_migrate` before attempting to create the table based on this function's return value. |
| `django/db/migrations/executor.py::MigrationExecutor.apply_migration` | medium | This function triggers the problematic behavior, but the core logic error of ignoring the DB router is in the downstream `MigrationRecorder`. | Consider guarding the call to `self.record_migration` with an `allow_migrate` check, although the fix is better placed in `MigrationRecorder`. |

**✗ Rejected**

| function | confidence | reason | edit_hint |
|----------|------------|--------|-----------|
| `django/db/migrations/recorder.py::MigrationRecorder.applied_migrations` | high | This function is not on the causal path to the symptom; its handling of a missing table is correct and does not trigger table creation. |  |

**Causal chains (per candidate)**

- `django/db/migrations/recorder.py::MigrationRecorder.has_table`  (score=6.0)  \
  django/test/runner.py::setup_databases calls migrate for each DB → django/db/migrations/executor.py::MigrationExecutor.apply_migration is called → apply_migration calls self.record_migration() → record_migration calls self.recorder.record_applied() → record_applied calls self.ensure_schema() → ensure_schema calls self.has_table()
- `django/db/migrations/recorder.py::MigrationRecorder.applied_migrations`  (score=0.0)  \
  
- `django/db/migrations/executor.py::MigrationExecutor.apply_migration`  (score=7.0)  \
  django/test/runner.py::setup_databases calls migrate for each DB → django/db/migrations/executor.py::MigrationExecutor.apply_migration is called for a non-default DB → apply_migration unconditionally calls self.record_migration() → This triggers the downstream sequence in MigrationRecorder that ignores the DB router and attempts to create a table

**next_to_explore:** `['django/db/migrations/recorder.py::MigrationRecorder.ensure_schema', 'django/db/migrations/executor.py::MigrationExecutor.record_migration', 'django/db/backends/base/schema.py::BaseDatabaseSchemaEditor.create_model', 'django/db/utils.py::ConnectionRouter.allow_migrate', 'django/test/runner.py::setup_databases']`

## Stage 5 — Listwise rerank decisions

### Rerank pass #1

| # | id | confidence |
|---|----|------------|
| 1 | `django/db/migrations/recorder.py::MigrationRecorder.ensure_schema` | 0.95 |
| 2 | `django/db/migrations/executor.py::MigrationExecutor.apply_migration` | 0.75 |
| 3 | `django/db/migrations/recorder.py::MigrationRecorder.record_applied` | 0.7 |
| 4 | `django/db/migrations/recorder.py::MigrationRecorder.has_table` | 0.1 |
| 5 | `django/db/utils.py::ConnectionRouter.allow_migrate` | 0.05 |
| 6 | `django/db/migrations/recorder.py::MigrationRecorder.applied_migrations` | 0.0 |
| 7 | `django/db/migrations/executor.py::MigrationExecutor.record_migration` | 0.0 |
| 8 | `django/db/migrations/recorder.py::MigrationRecorder.Migration` | 0.0 |
| 9 | `django/db/migrations/loader.py::MigrationLoader.check_consistent_history` | 0.0 |
| 10 | `django/db/migrations/executor.py::MigrationExecutor.unapply_migration` | 0.0 |

## Final ranked predictions (after consistency vote)

| # | function | score | confidence | runs | lines |
|---|----------|-------|------------|------|-------|
| 1 | `django/db/migrations/recorder.py::MigrationRecorder.ensure_schema` | 0.950 | high | 1/1 | (59, 70) |
| 2 | `django/db/migrations/executor.py::MigrationExecutor.apply_migration` | 0.750 | high | 1/1 | (222, 245) |
| 3 | `django/db/migrations/recorder.py::MigrationRecorder.record_applied` | 0.700 | high | 1/1 | (84, 87) |
| 4 | `django/db/migrations/recorder.py::MigrationRecorder.__init__` | 0.436 | high | 1/1 | (46, 47) |
| 5 | `django/db/migrations/executor.py::MigrationExecutor.detect_soft_applied` | 0.431 | high | 1/1 | (289, 381) |
| 6 | `django/db/migrations/recorder.py::MigrationRecorder.record_unapplied` | 0.424 | high | 1/1 | (89, 92) |
| 7 | `django/db/migrations/loader.py::MigrationLoader.add_internal_dependencies` | 0.421 | high | 1/1 | (187, 195) |
| 8 | `django/db/migrations/loader.py::MigrationLoader.migrations_module` | 0.417 | high | 1/1 | (56, 66) |
| 9 | `django/db/migrations/recorder.py::MigrationRecorder.has_table` | 0.100 | high | 1/1 | (53, 57) |
| 10 | `django/db/utils.py::ConnectionRouter.allow_migrate` | 0.050 | high | 1/1 | (272, 284) |
