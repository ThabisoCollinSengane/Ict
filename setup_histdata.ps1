# Extracts HistData zip/folder files from C:\Ict and renames them to
# the format expected by run_backtest_histdata.py (e.g. EURUSD_2022.csv)

$dest = "C:\Ict\data\histdata"
New-Item -ItemType Directory -Path $dest -Force | Out-Null

# Extract any zip files first
Get-ChildItem "C:\Ict" -Filter "HISTDATA_COM_ASCII_*.zip" | ForEach-Object {
    Write-Host "Extracting $($_.Name)..."
    Expand-Archive -Path $_.FullName -DestinationPath $dest -Force
}

# Copy CSVs from already-extracted folders
Get-ChildItem "C:\Ict" -Filter "HISTDATA_COM_ASCII_*" -Directory | ForEach-Object {
    Get-ChildItem $_.FullName -Filter "*.csv" | ForEach-Object {
        $parts = $_.BaseName -split "_"
        if ($parts.Length -ge 5) {
            $pair    = $parts[2]
            $year    = $parts[4]
            $newname = $pair + "_" + $year + ".csv"
            $target  = Join-Path $dest $newname
            Write-Host "Copying $($_.Name) -> $newname"
            Copy-Item $_.FullName $target -Force
        }
    }
}

Write-Host ""
Write-Host "Done. Files in $dest :"
Get-ChildItem $dest -Filter "*.csv" | Select-Object Name | Format-Table -HideTableHeaders
