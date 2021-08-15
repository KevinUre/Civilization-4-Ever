# Civilization 4-Ever

This is a mod for Civilization 4: Beyond the Sword that aims to balance and enhance the civ 4 experience while leaving the core spirit of the game intact.

## How to Install

Download a zip from the [Releases Page](https://github.com/KevinUre/Civilization-4-Ever/releases). Some releases also include the debugging DLL, but it's not mandatory. The latest version is always on top. Navigate to your Beyond the Sword mods folder (i.e. `\SteamApps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\`). Unzip the package to its own subdirectory. rename that directory to `Civilization 4-Ever`. Your path to the ini should now look like `\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Mods\Civilization 4-Ever\Civilization 4-Ever.ini`.

To boot the mod either boot the game and then goto `Advanced` then `Load a Mod` or make a shortcut to `Civ4BeyondSword.exe` and add ` mod= mods\Civilization 4-Ever` to the target. you can also add ` mod= mods\Civilization 4-Ever` to the launch options on steam.

## How to clear the game cache

The game caches some values when it runs and clearing this cache out seems to both fix problems when updating the mod as well as cure some multiplayer desyncs. Make sure the game is closed before you clear the cache.

Inside the mod directory there is a script `Clear-Cache.bat` that will clear the cache.

If you want to do it manually you can navigate to `%localappdata%\My Games\beyond the sword` and delete the `cache` directory found there.

## How to build

Run the Installer from the root. modify the `makefile` on lines `34` and `35` to the directory you used with the installer. put your path to your civ4 on line `42`. build with visual studio.
