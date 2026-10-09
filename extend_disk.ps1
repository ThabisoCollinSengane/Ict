# Extends C: partition to use all available unallocated space on the disk.
# Run as Administrator in PowerShell.

$maxSize = (Get-PartitionSupportedSize -DriveLetter C).SizeMax
Resize-Partition -DriveLetter C -Size $maxSize
Write-Host "Done. New C: size:"
Get-Partition -DriveLetter C | Select-Object Size
