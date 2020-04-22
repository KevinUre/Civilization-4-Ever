$btsPath = "D:\Games\Sid Meier's Civilization 4\Beyond the Sword"
$modssubdirectory = "Mods\Civilization 4-Ever\Assets"
$assetsDir = (Join-Path $btsPath $modssubdirectory )

$scriptDir = (Split-Path $script:MyInvocation.MyCommand.Path)
$sourceFile = (Join-Path $scriptDir "CvGameCoreDLL\Debug\CvGameCoreDLL.dll")
$destinationFile = (Join-Path $assetsDir "CvGameCoreDLL.dll")

Copy-Item -Path $sourceFile -Destination $destinationFile -Force
