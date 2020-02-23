#
# Air Combat Experience
# CvAirCombatExperienceEventManager
# 

from CvPythonExtensions import *

import CvUtil
import CvEventManager
import sys
import PyHelpers
import CvConfigParser
import math
import time
			
gc = CyGlobalContext()	

PyPlayer = PyHelpers.PyPlayer
PyGame = PyHelpers.PyGame()

localText = CyTranslator()

# Enables or disables route destruction through air bombs.
# Default value is true
g_bRouteDestructionThroughAirBombs = true

# Enables or disables experience gain from destroying improvements.
# Default value is true
g_bExperienceGainByDestroyingImprovements = true

# Enables or disables experience gain from destroying Routes. 
# Default value is true
g_bExperienceGainByDestroyingRoutes = true

# Enables or disables experience gain from bombing cities.
# Default value is true
g_bExperienceGainByAttackingCities = true

# Enables or disables experience game from attacking units.
# Default value is true
g_bExperienceGainByAttackingUnits = true

# Enables or disables the ability for air units to bomb no mans land.
# Default value is true
g_bBombNoMansLand = true

def loadConfigurationData():
	global g_bRouteDestructionThroughAirBombs
	global g_bExperienceGainByDestroyingImprovements
	global g_bExperienceGainByDestroyingRoutes
	global g_bExperienceGainByAttackingCities
	global g_bExperienceGainByAttackingUnits
	global g_bBombNoMansLand
	
	config = CvConfigParser.CvConfigParser("Air Combat Experience Config.ini")

	if(config != None):
		g_bRouteDestructionThroughAirBombs = config.getboolean("Air Combat Experience", "Route Destruction Through Air Bombs", true)
		g_bExperienceGainByDestroyingImprovements = config.getboolean("Air Combat Experience", "Experience Gain By Destroying Improvements", true)
		g_bExperienceGainByDestroyingRoutes = config.getboolean("Air Combat Experience", "Experience Gain By Destroying Routes", true)
		g_bExperienceGainByAttackingCities = config.getboolean("Air Combat Experience", "Experience Gain By Attacking Cities", true)
		g_bExperienceGainByAttackingUnits = config.getboolean("Air Combat Experience", "Experience Gain By Attacking Units", true)
		g_bBombNoMansLand = config.getboolean("Air Combat Experience", "Bomb No Mans Land", true)

 	gc.getGame().setRouteDestructionThroughAirBombs(g_bRouteDestructionThroughAirBombs);
 	gc.getGame().setExperienceGainByDestroyingImprovements(g_bExperienceGainByDestroyingImprovements);
 	gc.getGame().setExperienceGainByDestroyingRoutes(g_bExperienceGainByDestroyingRoutes);
 	gc.getGame().setExperienceGainByAttackingCities(g_bExperienceGainByAttackingCities);
 	gc.getGame().setExperienceGainByAttackingUnits(g_bExperienceGainByAttackingUnits);
	gc.getGame().setBombNoMansLand(g_bBombNoMansLand)
		
class CvAirCombatExperienceEventManager:
	
	def __init__(self, eventManager):

		eventManager.addEventHandler("GameStart", self.onGameStart)
		eventManager.addEventHandler("windowActivation", self.onWindowActivation)
		#eventManager.addEventHandler("mouseEvent", self.onMouseEvent)

		loadConfigurationData()

	def onMouseEvent(self, argsList):
		eventType,mx,my,px,py,interfaceConsumed,screens = argsList

		if ( eventType == 1 ):
			CyInterface().addImmediateMessage("g_bRouteDestructionThroughAirBombs %s %s" %(g_bRouteDestructionThroughAirBombs, gc.getGame().isRouteDestructionThroughAirBombs()),"")

	def onWindowActivation(self, argsList):
		'Called when the game window activates or deactivates'
		bActive = argsList[0]
		
		if(bActive):
			loadConfigurationData()	
	
		
	def onGameStart(self, argsList):
		loadConfigurationData()
