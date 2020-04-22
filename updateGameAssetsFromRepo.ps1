$btsPath = "D:\Games\Sid Meier's Civilization 4\Beyond the Sword"
$modssubdirectory = "Mods\Civilization 4-Ever"

$scriptDir = (Split-Path $script:MyInvocation.MyCommand.Path)
$sourceDir =  (Join-Path  $scriptDir "mod-components")
$destinationDir = (Join-Path $btsPath $modssubdirectory )

Remove-Item $destinationDir -Force -Recurse
Write-Host $sourceDir
Write-Host $destinationDir
Get-ChildItem -Path $sourceDir
Get-ChildItem -Path $sourceDir -Recurse | Copy-Item -Destination {
    if ($_.PSIsContainer) {
        Join-Path $to $_.Parent.FullName.Substring($from.length)
    } else {
        Join-Path $to $_.FullName.Substring($from.length)
    }
}
Get-ChildItem -Path $destinationDir

# Remove-Item "D:\Games\Sid Meier's Civilization 4\Beyond the Sword\Mods\Civilization 4-Ever" -Force -Recurse
# Get-ChildItem -Path .\mod-components | Copy-Item -Destination "D:\Games\Sid Meier's Civilization 4\Beyond the Sword\Mods\Civilization 4-Ever" -Recurse