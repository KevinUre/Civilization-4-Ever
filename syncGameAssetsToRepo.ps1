$btsPath = "D:\Games\Sid Meier's Civilization 4 - Bare\Beyond the Sword"
$modssubdirectory = "Mods\Civilization 4-Ever\Assets"

$basedir = (Join-Path $btsPath $modssubdirectory )

Copy-Item (Join-Path $basedir "Art") -Destination (Join-Path $PSScriptRoot "game-assets") -Force
Copy-Item (Join-Path $basedir "CvGameCoreDLL") -Destination (Join-Path $PSScriptRoot "game-assets") -Force
Copy-Item (Join-Path $basedir "Python") -Destination (Join-Path $PSScriptRoot "game-assets") -Force
Copy-Item (Join-Path $basedir "XML") -Destination (Join-Path $PSScriptRoot "game-assets") -Force