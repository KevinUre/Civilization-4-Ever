# $btsPath = "D:\Games\Sid Meier's Civilization 4\Beyond the Sword"
# $modssubdirectory = "Mods\Civilization 4-Ever\*"

# $scriptDir = (Split-Path $script:MyInvocation.MyCommand.Path)
# $sourceDir = (Join-Path $btsPath $modssubdirectory )
# $destinationDir = (Join-Path  $scriptDir "mod-components")

# Remove-Item $destinationDir -Force -Recurse
# Copy-Item -Path $sourceDir -Destination $destinationDir -Force -Recurse

Remove-Item .\mod-components -Force -Recurse
Get-ChildItem -Path "D:\Games\Sid Meier's Civilization 4\Beyond the Sword\Mods\Civilization 4-Ever" | Copy-Item -Destination .\mod-components -Recurse
