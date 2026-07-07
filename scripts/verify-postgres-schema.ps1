[CmdletBinding()]
param(
    [ValidateRange(10, 120)]
    [int]$StartupTimeoutSeconds = 60
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$composeFile = Join-Path $repositoryRoot "infra\postgres\compose.integration.yaml"
$migrationFile = Join-Path $repositoryRoot "infra\postgres\migrations\0001_ledger_schema.sql"

foreach ($requiredPath in @($composeFile, $migrationFile)) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        throw "Required file was not found: $requiredPath"
    }
}

& docker info *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker Desktop is not reachable. Start Docker Desktop and retry."
}

& docker compose version *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker Compose is not available. Install or enable Docker Compose and retry."
}

$projectName = "compose-release-assurance-postgres-integration-$PID"
$composeBaseArguments = @("-p", $projectName, "-f", $composeFile)
$environmentNames = @("POSTGRES_DB", "POSTGRES_PASSWORD", "POSTGRES_USER")
$previousEnvironment = @{}

foreach ($environmentName in $environmentNames) {
    $previousEnvironment[$environmentName] = [Environment]::GetEnvironmentVariable(
        $environmentName,
        "Process"
    )
}

$randomBytes = New-Object byte[] 24
$randomNumberGenerator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
try {
    $randomNumberGenerator.GetBytes($randomBytes)
}
finally {
    $randomNumberGenerator.Dispose()
}

$env:POSTGRES_DB = "ledger_test"
$env:POSTGRES_USER = "ledger_test"
$env:POSTGRES_PASSWORD = [Convert]::ToBase64String($randomBytes)

$cleanupRequired = $false

function Invoke-Compose {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    & docker compose @composeBaseArguments @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose command failed: docker compose $($Arguments -join ' ')"
    }
}

function Invoke-PsqlCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string]$Sql
    )

    & docker compose @composeBaseArguments exec -T postgres psql `
        -X `
        --set=ON_ERROR_STOP=1 `
        --username $env:POSTGRES_USER `
        --dbname $env:POSTGRES_DB `
        --command $Sql

    if ($LASTEXITCODE -ne 0) {
        throw "PostgreSQL command failed: $Name"
    }

    Write-Host "PASS: $Name"
}

function Get-PsqlScalar {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Sql
    )

    $output = & docker compose @composeBaseArguments exec -T postgres psql `
        -X `
        --tuples-only `
        --no-align `
        --quiet `
        --set=ON_ERROR_STOP=1 `
        --username $env:POSTGRES_USER `
        --dbname $env:POSTGRES_DB `
        --command $Sql

    if ($LASTEXITCODE -ne 0) {
        throw "PostgreSQL scalar query failed."
    }

    return ($output | Out-String).Trim()
}

function Assert-DatabaseConstraintRejects {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string]$Sql,

        [Parameter(Mandatory = $true)]
        [string]$ExpectedConstraintName
    )

    $writeSql = $Sql.Trim()
    if (-not $writeSql.EndsWith(";")) {
        $writeSql += ";"
    }

    $escapedName = $Name.Replace("'", "''")
    $escapedConstraintName = $ExpectedConstraintName.Replace("'", "''")

    # Keep expected-failure handling inside PostgreSQL. This avoids making
    # PowerShell parse psql stderr for a successful negative test.
    $assertionSql = @'
DO $assertion$
DECLARE
    observed_constraint TEXT;
BEGIN
    BEGIN
__WRITE_SQL__
        RAISE EXCEPTION USING
            ERRCODE = 'P0001',
            MESSAGE = 'Expected rejected write was accepted.';
    EXCEPTION
        WHEN OTHERS THEN
            GET STACKED DIAGNOSTICS observed_constraint = CONSTRAINT_NAME;

            IF SQLSTATE = 'P0001'
               AND SQLERRM = 'Expected rejected write was accepted.'
            THEN
                RAISE EXCEPTION 'PostgreSQL accepted an invalid write: __NAME__';
            END IF;

            IF observed_constraint IS DISTINCT FROM '__CONSTRAINT_NAME__' THEN
                RAISE EXCEPTION
                    'Unexpected constraint for __NAME__. Expected %, got %.',
                    '__CONSTRAINT_NAME__',
                    COALESCE(observed_constraint, '<none>');
            END IF;
    END;
END
$assertion$;
'@

    $assertionSql = $assertionSql.Replace("__WRITE_SQL__", $writeSql)
    $assertionSql = $assertionSql.Replace("__NAME__", $escapedName)
    $assertionSql = $assertionSql.Replace(
        "__CONSTRAINT_NAME__",
        $escapedConstraintName
    )

    Invoke-PsqlCommand -Name "$Name was rejected." -Sql $assertionSql
}

try {
    # Cleanup must also run when Compose creates partial resources before failing.
    $cleanupRequired = $true
    Invoke-Compose -Arguments @("up", "--detach", "--remove-orphans")

    $deadline = (Get-Date).AddSeconds($StartupTimeoutSeconds)
    $isReady = $false

    while ((Get-Date) -lt $deadline) {
        & docker compose @composeBaseArguments exec -T postgres pg_isready `
            --username $env:POSTGRES_USER `
            --dbname $env:POSTGRES_DB *> $null

        if ($LASTEXITCODE -eq 0) {
            $isReady = $true
            break
        }

        Start-Sleep -Seconds 2
    }

    if (-not $isReady) {
        throw "PostgreSQL did not become ready within $StartupTimeoutSeconds seconds."
    }

    $containerId = (
        & docker compose @composeBaseArguments ps --quiet postgres | Out-String
    ).Trim()

    if (-not $containerId) {
        throw "PostgreSQL container identifier could not be resolved."
    }

    & docker cp $migrationFile "${containerId}:/tmp/0001_ledger_schema.sql"
    if ($LASTEXITCODE -ne 0) {
        throw "The PostgreSQL migration could not be copied into the test container."
    }

    & docker compose @composeBaseArguments exec -T postgres psql `
        -X `
        --set=ON_ERROR_STOP=1 `
        --single-transaction `
        --username $env:POSTGRES_USER `
        --dbname $env:POSTGRES_DB `
        --file /tmp/0001_ledger_schema.sql

    if ($LASTEXITCODE -ne 0) {
        throw "The PostgreSQL migration failed."
    }

    Write-Host "PASS: versioned migration applied."

    Invoke-PsqlCommand -Name "valid synthetic ledger state" -Sql @"
BEGIN;
INSERT INTO transfers (
    id,
    request_fingerprint,
    debit_account_id,
    credit_account_id,
    amount,
    currency,
    created_at
) VALUES (
    'transfer-001',
    repeat('a', 64),
    'account-debit',
    'account-credit',
    25.00,
    'USD',
    now()
);

INSERT INTO idempotency_records (
    key,
    request_fingerprint,
    transfer_id,
    created_at
) VALUES (
    'idem-001',
    repeat('a', 64),
    'transfer-001',
    now()
);

INSERT INTO ledger_entries (
    id,
    transfer_id,
    direction,
    account_id,
    amount,
    currency,
    created_at
) VALUES
    (
        'entry-001',
        'transfer-001',
        'DEBIT',
        'account-debit',
        25.00,
        'USD',
        now()
    ),
    (
        'entry-002',
        'transfer-001',
        'CREDIT',
        'account-credit',
        25.00,
        'USD',
        now()
    );

INSERT INTO audit_records (
    id,
    transfer_id,
    event_type,
    correlation_id,
    occurred_at
) VALUES (
    'audit-001',
    'transfer-001',
    'TRANSFER_ACCEPTED',
    'runtime-schema-verification',
    now()
);
COMMIT;
"@

    $recordCounts = Get-PsqlScalar -Sql @"
SELECT concat_ws(
    '|',
    (SELECT count(*) FROM transfers),
    (SELECT count(*) FROM idempotency_records),
    (SELECT count(*) FROM ledger_entries),
    (SELECT count(*) FROM audit_records)
);
"@

    if ($recordCounts -ne "1|1|2|1") {
        throw "Unexpected valid-state record counts: $recordCounts"
    }

    Write-Host "PASS: valid-state record counts are 1|1|2|1."

    Assert-DatabaseConstraintRejects `
        -Name "duplicate idempotency key" `
        -ExpectedConstraintName "idempotency_records_pkey" `
        -Sql @"
INSERT INTO idempotency_records (
    key,
    request_fingerprint,
    transfer_id,
    created_at
) VALUES (
    'idem-001',
    repeat('b', 64),
    'transfer-001',
    now()
);
"@

    Assert-DatabaseConstraintRejects `
        -Name "duplicate idempotency transfer reference" `
        -ExpectedConstraintName "idempotency_records_transfer_id_key" `
        -Sql @"
INSERT INTO idempotency_records (
    key,
    request_fingerprint,
    transfer_id,
    created_at
) VALUES (
    'idem-002',
    repeat('b', 64),
    'transfer-001',
    now()
);
"@

    Assert-DatabaseConstraintRejects `
        -Name "second debit entry for one transfer" `
        -ExpectedConstraintName "ledger_entries_one_direction_per_transfer" `
        -Sql @"
INSERT INTO ledger_entries (
    id,
    transfer_id,
    direction,
    account_id,
    amount,
    currency,
    created_at
) VALUES (
    'entry-003',
    'transfer-001',
    'DEBIT',
    'account-debit',
    25.00,
    'USD',
    now()
);
"@

    Assert-DatabaseConstraintRejects `
        -Name "invalid transfer currency" `
        -ExpectedConstraintName "transfers_currency_check" `
        -Sql @"
INSERT INTO transfers (
    id,
    request_fingerprint,
    debit_account_id,
    credit_account_id,
    amount,
    currency,
    created_at
) VALUES (
    'transfer-invalid-currency',
    repeat('c', 64),
    'account-debit',
    'account-credit',
    10.00,
    'usd',
    now()
);
"@

    Assert-DatabaseConstraintRejects `
        -Name "matching debit and credit accounts" `
        -ExpectedConstraintName "transfers_distinct_accounts" `
        -Sql @"
INSERT INTO transfers (
    id,
    request_fingerprint,
    debit_account_id,
    credit_account_id,
    amount,
    currency,
    created_at
) VALUES (
    'transfer-matching-accounts',
    repeat('d', 64),
    'account-same',
    'account-same',
    10.00,
    'USD',
    now()
);
"@

    Assert-DatabaseConstraintRejects `
        -Name "orphan ledger entry" `
        -ExpectedConstraintName "ledger_entries_transfer_id_fkey" `
        -Sql @"
INSERT INTO ledger_entries (
    id,
    transfer_id,
    direction,
    account_id,
    amount,
    currency,
    created_at
) VALUES (
    'entry-orphan',
    'missing-transfer',
    'DEBIT',
    'account-debit',
    10.00,
    'USD',
    now()
);
"@

    Assert-DatabaseConstraintRejects `
        -Name "second audit record for one transfer" `
        -ExpectedConstraintName "audit_records_one_per_transfer" `
        -Sql @"
INSERT INTO audit_records (
    id,
    transfer_id,
    event_type,
    correlation_id,
    occurred_at
) VALUES (
    'audit-002',
    'transfer-001',
    'TRANSFER_ACCEPTED',
    'runtime-schema-verification',
    now()
);
"@

    $finalRecordCounts = Get-PsqlScalar -Sql @"
SELECT concat_ws(
    '|',
    (SELECT count(*) FROM transfers),
    (SELECT count(*) FROM idempotency_records),
    (SELECT count(*) FROM ledger_entries),
    (SELECT count(*) FROM audit_records)
);
"@

    if ($finalRecordCounts -ne "1|1|2|1") {
        throw "Rejected writes changed persisted state: $finalRecordCounts"
    }

    Write-Host "PASS: rejected writes did not change persisted state."
    Write-Host "PASS: PostgreSQL runtime schema verification completed."
}
catch {
    $originalFailure = $_

    if ($cleanupRequired) {
        Write-Host "PostgreSQL integration container state after failure:"

        $previousErrorActionPreference = $ErrorActionPreference
        try {
            $ErrorActionPreference = "Continue"
            & docker compose @composeBaseArguments ps 2>&1 |
                ForEach-Object { Write-Host $_ }
        }
        finally {
            $ErrorActionPreference = $previousErrorActionPreference
        }
    }

    throw $originalFailure
}
finally {
    $cleanupExitCode = 0
    $cleanupOutput = ""

    if ($cleanupRequired) {
        $previousErrorActionPreference = $ErrorActionPreference
        try {
            # Compose progress can be emitted on stderr even when cleanup succeeds.
            # Cleanup must not mask the original verification result.
            $ErrorActionPreference = "Continue"

            $cleanupOutput = & docker compose @composeBaseArguments down `
                --volumes `
                --remove-orphans 2>&1 | Out-String

            $cleanupExitCode = $LASTEXITCODE
        }
        finally {
            $ErrorActionPreference = $previousErrorActionPreference
        }

        if ($cleanupExitCode -ne 0) {
            Write-Warning (
                "PostgreSQL integration cleanup returned exit code " +
                "$cleanupExitCode. Output: $($cleanupOutput.Trim())"
            )
        }
    }

    foreach ($environmentName in $environmentNames) {
        $previousValue = $previousEnvironment[$environmentName]
        if ($null -eq $previousValue) {
            Remove-Item "Env:$environmentName" -ErrorAction SilentlyContinue
        }
        else {
            Set-Item "Env:$environmentName" -Value $previousValue
        }
    }
}
