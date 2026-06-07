# Renames DAT_ASCII_EURUSD_M1_2022.csv → EURUSD_2022.csv in data\histdata\

$dir = "C:\Ict\data\histdata"

Get-ChildItem $dir -Filter "DAT_ASCII_*_M1_*.csv" | ForEach-Object {
    $parts   = $_.BaseName -split "_"
    $pair    = $parts[2]
    $year    = $parts[4]
    $newname = $pair + "_" + $year + ".csv"
    Write-Host ("Renaming " + $_.Name + " -> " + $newname)
    Rename-Item $_.FullName (Join-Path $dir $newname)
}

Write-Host ""
Write-Host "Done. Files now:"
Get-ChildItem $dir -Filter "*.csv" | Select-Object Name | Format-Table -HideTableHeaders
