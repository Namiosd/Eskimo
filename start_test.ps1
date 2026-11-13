param(
    [Parameter(Position=0)]
    [string]$Target = "tests/test_login.py",
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$ExtraArgs
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $ScriptDir
try {
    # 1. Run test suite via run_tests.py
    python run_tests.py --target "$Target" --locale en --platform android @ExtraArgs
    $TestExitCode = $LASTEXITCODE

    # 2. Get latest timestamped directory in logs/
    $LatestDir = Get-ChildItem -Path "logs" -Directory | Sort-Object Name -Descending | Select-Object -First 1
    if ($null -ne $LatestDir) {
        $RunLogDir = "logs/$($LatestDir.Name)"
        # 3. Generate report.html from suite.log
        python generate_report.py --log "$RunLogDir/suite.log" --output "$RunLogDir/report.html"
        # 4. Print path
        Write-Host "Report generated at $RunLogDir/report.html" -ForegroundColor Green
    }
    exit $TestExitCode
}
finally {
    Pop-Location
}

