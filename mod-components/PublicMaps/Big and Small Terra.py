##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##	File:	 NewWorld.py
##	Author:  Sean McCarthy (SevenSpirits)
##	Version: 1.0
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator
from math import sqrt
from array import array

def getDescription():
	return "Hemispheres-like map script with mixed-in islands a la Big and Small and options to include a New World"

def isAdvancedMap():
	"This map should not show up in simple mode"
	return 0

def getNumCustomMapOptions():
	return 4
	
def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_SCRIPT_CONTINENTS_SIZE",
		1:	"Island Count",
		2:	"Continent Regions",
		3:	"Force New World"
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	5,
		1:	3,
		2:	2,
		3:	2
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "Massive Continents",
			1: "Normal Continents",
			2: "Snaky Continents",
			3: "Archipelago",
			4: "Varied"
			},
		1:	{
			0: "Few",
			1: "Normal",
			2: "Many"
			},
		2:	{
			0: "2",
			1: "3"
			},
		3:	{
			0: "Yes",
			1: "No"
			}
		}

	translated_text = selection_names[iOption][iSelection]
	return translated_text

def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	1,
		1:	1,
		2:	0,
		3:	0
		}
	return option_defaults[iOption]

def minStartingDistanceModifier():
	return -12

def getGridSize(argsList):
	"Bigger grid sizes due to new world emptiness"
	grid_sizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:		  (14,9),
			WorldSizeTypes.WORLDSIZE_TINY:		  (18,11),
			WorldSizeTypes.WORLDSIZE_SMALL:		 (24,15),
			WorldSizeTypes.WORLDSIZE_STANDARD:	  (28,18),
			WorldSizeTypes.WORLDSIZE_LARGE:		 (34,21),
			WorldSizeTypes.WORLDSIZE_HUGE:		  (38,24)
	}
	if (argsList[0] == -1): # (-1,) is passed to function on loads
			return []
	[eWorldSize] = argsList
	return grid_sizes[eWorldSize]

def beforeGeneration():
	global xShiftRoll
	global yShiftRoll
	global ySplitRoll
	global yPortionRoll
	gc = CyGlobalContext()
	dice = gc.getGame().getMapRand()

	# Binary shift roll (for horizontal shifting if Island Region Separate).
	xShiftRoll = dice.get(2, "Region Shift, Horizontal - Left and Right PYTHON")
	yShiftRoll = dice.get(2, "Region Shift, Vertical - Left and Right PYTHON")
	ySplitRoll = dice.get(2, "Region Split, Vertical - Left and Right PYTHON")
	yPortionRoll = dice.get(2, "Region Portioning, Vertical - Left and Right PYTHON")
	print xShiftRoll

am = None
am2 = None
newWorldID = 0
oldWorldCount = 1
isBigNewWorld = True

#force all players to start on old world
def findStartingPlot(argsList):
	[playerID] = argsList

	def isValid(playerID, x, y):
		global am
		global am2
		global newWorldID
		
		if am == None:
			setupAreaMap()
		if am.areaMap[am.getIndex(x,y)] == newWorldID:
			return False
		
		#also disallow starting on small islands
		if am2 == None: 
			setupAreaMap2()
		if am2.getAreaByID(am2.areaMap[am2.getIndex(x,y)]).size < 70:
			return False

		return True
	
	return CvMapGeneratorUtil.findStartingPlot(playerID, isValid)

def setupAreaMap():
	global am
	global newWorldID
	print "init areamap..."
	map = CyMap()
	
	am = Areamap(map.getGridWidth(),map.getGridHeight())
	am.defineAreas(True)
	newWorldID = am.getNewWorldID()
	
	print "...done"
def setupAreaMap2():
	global am2
	print "init areamap2..."
	map = CyMap()
	
	am2 = Areamap(map.getGridWidth(),map.getGridHeight())
	am2.defineAreas(False)
	print "...done2"
	
class BnSMultilayeredFractal(CvMapGeneratorUtil.MultilayeredFractal):
	def generateIslandRegion(self, minTinies, extraTinies, iWestX, iSouthY, iWidth, iHeight, iGrain):
		# Add a few random patches of Tiny Islands first.
		#TODO: Base numTinies on global prevalance option
		
		#We are not using this function!
		return 0
		
		numTinies = minTinies + self.dice.get(extraTinies, "Tiny Islands - Custom Continents PYTHON")
		print("Patches of Tiny Islands: ", numTinies)
		if numTinies:
			for tiny_loop in range(numTinies):
				tinyWidth = int(self.iW * 0.15)
				tinyHeight = int(self.iH * 0.15)

				tinyWestX = iWestX + self.dice.get(iWidth - tinyWidth, "Tiny Longitude - Custom Continents PYTHON")
				tinySouthY = iSouthY + self.dice.get(iHeight - tinyHeight, "Tiny Latitude - Custom Continents PYTHON")

				self.generatePlotsInRegion(80,
										   tinyWidth, tinyHeight,
										   tinyWestX, tinySouthY,
										   iGrain, 3,
										   0, self.iTerrainFlags,
										   6, 5,
										   True, 3,
										   -1, False,
										   False
										   )
		return 0

	def generateContinentRegion(self, iWater, iWidth, iHeight, iWestX, iSouthY, iGrain, xExp):
		#I have changed this function to place both continent-grade land as well as islands.
		#This is similar to what Big and Small does with the Islands Mixed In option.
		
		islandImportance = self.map.getCustomMapOption(1)

		#Since we are placing land twice we need to increase water % of each one
		#At normal island importance this is easily done by giving each the square root of
		#of the water fraction.
		#The other two settings are arranged such that either continents or islands gets 
		#twice as much land area as the other, while maintaining the same average total land to
		#water ratio.
		if islandImportance == 0:
			iContinentsWater = int(100.0*(sqrt(.02*iWater+.25) - .5))
			iIslandsWater    = 100 * iWater / iContinentsWater
		elif islandImportance == 1:
			iContinentsWater = int(sqrt(iWater/100.0)*100.0)
			iIslandsWater    = iContinentsWater
		elif islandImportance == 2:
			iIslandsWater    = int(100.0*(sqrt(.02*iWater+.25) - .5))
			iContinentsWater = 100 * iWater / iIslandsWater
		
		print("CONTINENT!")
		print("Region continentsWater: ",iContinentsWater,"Region islandsWater: ",iIslandsWater)
		print("West",iWestX,"South",iSouthY,"Width",iWidth,"Height",iHeight,"Grain",iGrain)
		
		self.generatePlotsInRegion(iContinentsWater,
								   iWidth, iHeight,
								   iWestX, iSouthY,
								   iGrain, 4,
								   self.iRoundFlags, self.iTerrainFlags,
								   7, 7,
								   True, 4,
								   -1, False,
								   False
								   )
		self.generatePlotsInRegion(iIslandsWater,
								   iWidth, iHeight,
								   iWestX, iSouthY,
								   4, 3,
								   self.iVertFlags, self.iTerrainFlags,
								   6, 6,
								   True, 3,
								   -1, False,
								   False
								   )
		return 0

	def generatePlotsByRegion(self):
		# Sirian's MultilayeredFractal class, controlling function.
		# You -MUST- customize this function for each use of the class.
		global xShiftRoll
		global yShiftRoll
		global ySplitRoll
		global yPortionRoll
		global am
		global am2
		global oldWorldCount
		global isBigNewWorld
		am = None
		am2 = None
		oldWorldCount = self.map.getCustomMapOption(2) + 2
		if self.map.getCustomMapOption(3) == 0:
			oldWorldCount -= 1
			isBigNewWorld = True
		else:
			isBigNewWorld = False

		print("getSeaLevelChange", self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange())

		if (self.map.getCustomMapOption(0) == 4):
			# Generate varied
			iContinentsGrain = 1
			iSecondaryContinentsGrain = 3
			iTertiaryContinentsGrain = 2
			iPrimaryWater = 74
			iSecondaryWater = 79
			iTertiaryWater = 76
		else:
			iContinentsGrain = 1 + self.map.getCustomMapOption(0)
			iSecondaryContinentsGrain = 1 + self.map.getCustomMapOption(0)
			iTertiaryContinentsGrain = 1 + self.map.getCustomMapOption(0)
			iPrimaryWater = 74
			iSecondaryWater = 74
			iTertiaryWater = 74

		iPrimaryWater += self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()
		iSecondaryWater += self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()
		iTertiaryWater += self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()

		splitYBigger = 0.5
		splitYSmaller = 0.5
		splitYBuffer = 0.1

		iIslandsGrain = 3
		tinyIslandOverlap = 0
		regions = self.map.getCustomMapOption(2) + 2
		if (regions == 2):
			vSplitPrimary = 0
			vSplitSecondary = 0
			vSplitTertiary = 0
			tripleSplit = 0
		elif (regions == 3):
			vSplitPrimary = 0
			vSplitSecondary = 0
			vSplitTertiary = 0
			tripleSplit = 1
		else:
			#unexpected
			vSplitPrimary = 0
			vSplitSecondary = 0
			vSplitTertiary = 0
			tripleSplit = 0

		# Water variables need to differ if Overlap is set. Defining default here.
		#TODO: Set this from the global option
		#iWater = 74

		# Base values for full map
		iSouthY = 0
		iNorthY = self.iH - 1
		iHeight = iNorthY - iSouthY + 1
		iWestX = 0
		iEastX = self.iW - 1
		iWidth = iEastX - iWestX + 1
		print("Cont South: ", iSouthY, "Cont North: ", iNorthY, "Cont Height: ", iHeight)

		if tinyIslandOverlap:
			self.generateIslandRegion(4, 6, iWestX, iSouthY, iWidth, iHeight, iIslandsGrain)

		# Add the Continents.
		# Horizontal dimensions may be affected by overlap and/or shift.
		# The regions are separate, with continents only in one part, islands only in the other.
		# Set X exponent to square setting:
		xExp = 6
		# Handle horizontal shift for the Continents layer.
		# (This will choose one side or the other for this region then fit it properly in its space).
		if tripleSplit:
			if xShiftRoll:
				westShift = int(0.33 * self.iW)
				eastShift = int(0.33 * self.iW)
			else:
				westShift = 0
				eastShift = int(0.66 * self.iW)
		else:
			if xShiftRoll:
				westShift = int(0.5 * self.iW)
				eastShift = 0
			else:
				westShift = 0
				eastShift = int(0.5 * self.iW)
		
		iWestX = westShift
		iEastX = self.iW - eastShift
		iWidth = iEastX - iWestX

		# Only one primary region
		iSouthY = 0
		iNorthY = self.iH - 1
		iHeight = iNorthY - iSouthY + 1
		print("Cont West: ", iWestX, "Cont East: ", iEastX, "Cont Width: ", iWidth)
		self.generateContinentRegion(iPrimaryWater, iWidth, iHeight, iWestX, iSouthY, iContinentsGrain, xExp)

		# Add the Secondary continents.
		# Horizontal dimensions may be affected by overlap and/or shift.
		# The regions are separate, with continents only in one part, islands only in the other.
		# Set X exponent to square setting:
		xExp = 6
		# Handle horizontal shift for the Continents layer.
		# (This will choose one side or the other for this region then fit it properly in its space).
		if tripleSplit:
			if xShiftRoll:
				westShift = 0
				eastShift = int(0.66 * self.iW)
			else:
				westShift = int(0.33 * self.iW)
				eastShift = int(0.33 * self.iW)
		else:
			if xShiftRoll:
				westShift = 0
				eastShift = int(0.5 * self.iW)
			else:
				westShift = int(0.5 * self.iW)
				eastShift = 0

		iWestX = westShift
		iEastX = self.iW - eastShift
		iWidth = iEastX - iWestX


		# Only one secondary region
		iSouthY = 0
		iNorthY = self.iH - 1
		iHeight = iNorthY - iSouthY + 1
		print("Island West: ", iWestX, "Island East: ", iEastX, "Isl Width: ", iWidth)
		self.generateContinentRegion(iSecondaryWater, iWidth, iHeight, iWestX, iSouthY, iSecondaryContinentsGrain, xExp)
		
		if tripleSplit:
			# Add the Tertiary continents.
			# Horizontal dimensions may be affected by overlap and/or shift.
			# The regions are separate, with continents only in one part, islands only in the other.
			# Set X exponent to square setting:
			xExp = 6
			# Handle horizontal shift for the Continents layer.
			# (This will choose one side or the other for this region then fit it properly in its space).
			westShift = int(0.66 * self.iW)
			eastShift = 0
			
			iWestX = westShift
			iEastX = self.iW - eastShift
			iWidth = iEastX - iWestX

			# Only one tertiary region
			iSouthY = 0
			iNorthY = self.iH - 1
			iHeight = iNorthY - iSouthY + 1
			print("Island West: ", iWestX, "Island East: ", iEastX, "Isl Width: ", iWidth)
			self.generateContinentRegion(iTertiaryWater, iWidth, iHeight, iWestX, iSouthY, iTertiaryContinentsGrain, xExp)

			if (tinyIslandOverlap == 0):
				self.generateIslandRegion(3, 4, iWestX, iSouthY, iWidth, iHeight, iIslandsGrain)

		
		# All regions have been processed. Plot Type generation completed.
		print "Done"
		return self.wholeworldPlotTypes

'''
Regional Variables Key:

iWaterPercent,
iRegionWidth, iRegionHeight,
iRegionWestX, iRegionSouthY,
iRegionGrain, iRegionHillsGrain,
iRegionPlotFlags, iRegionTerrainFlags,
iRegionFracXExp, iRegionFracYExp,
bShift, iStrip,
rift_grain, has_center_rift,
invert_heights
'''

def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Custom Continents) ...")
	fractal_world = BnSMultilayeredFractal()
	plotTypes = fractal_world.generatePlotsByRegion()
	return plotTypes

def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python Custom Continents) ...")
	terraingen = TerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

def addFeatures():
	NiTextOut("Adding Features (Python Custom Continents) ...")
	featuregen = FeatureGenerator()
	featuregen.addFeatures()
	return 0



#Borrowed from PerfectWorld.py by Rich Marinaccio (see http://forums.civfanatics.com/showthread.php?t=239982)
##############################################################################
## Custom Area tracker allows for considering coast as land to find
## 'New World' type continents that cannot be reached with galleys.
## Also used for filling in lakes since the required code is similar
##############################################################################
class Areamap :
	def __init__(self,width,height):
		self.mapWidth = width
		self.mapHeight = height
		self.areaMap = array('i')
		#initialize map with zeros
		for i in range(0,self.mapHeight*self.mapWidth):
			self.areaMap.append(0)
		self.map = CyMap()
		self.COAST = CyGlobalContext().getInfoTypeForString("TERRAIN_COAST")
		return
	def defineAreas(self,coastIsLand):
		#coastIsLand = True means that we are trying to find continents that
		#are not connected by coasts to the main landmasses, allowing us to
		#find continents suitable as a 'New World'. Otherwise, we
		#are just looking to fill in lakes and coast needs to be considered
		#water in that case
#		self.areaSizes = array('i')
		self.areaList = list()
		areaID = 0
		#make sure map is erased in case it is used multiple times
		for i in range(0,self.mapHeight*self.mapWidth):
			self.areaMap[i] = 0
#		for i in range(0,1):
		for i in range(0,self.mapHeight*self.mapWidth):
			if self.areaMap[i] == 0: #not assigned to an area yet
				areaID += 1
				areaSize,isWater = self.fillArea(i,areaID,coastIsLand)
				area = Area(areaID,areaSize,isWater)
				self.areaList.append(area)
		return

	def isWater(self,x,y,coastIsLand):
		#coastIsLand = True means that we are trying to find continents that
		#are not connected by coasts to the main landmasses, allowing us to
		#find continents suitable as a 'New World'. Otherwise, we
		#are just looking to fill in lakes and coast needs to be considered
		#water in that case
		ii = self.getIndex(x,y)
		if not (self.map.plot(x, y).isWater()):
			return False
		
		plotType = self.map.plot(x, y).getTerrainType()
		
		if coastIsLand and (plotType == self.COAST):
			return False
			
		return True
		
	def getAreaByID(self,areaID):
		for i in range(len(self.areaList)):
			if self.areaList[i].ID == areaID:
				return self.areaList[i]
		return None
	def getOceanID(self):
#		self.areaList.sort(key=operator.attrgetter('size'),reverse=True)
		self.areaList.sort(lambda x,y:cmp(x.size,y.size))
		self.areaList.reverse()
		for a in self.areaList:
			if a.water == True:
				return a.ID
	
	def getNewWorldID(self):
		global oldWorldCount
		global isBigNewWorld
		
		#self.PrintAreaMap()
		nID = 0
		continentList = list()
		for a in self.areaList:
			if a.water == False:
				continentList.append(a)

		totalLand = 0			 
		for c in continentList:
			totalLand += c.size
			
		print totalLand

		#sort all the continents by size, largest first
		continentList.sort(lambda x,y:cmp(y.size,x.size))

		print ''
		print "All continents"
		print self.PrintList(continentList)

		#now remove n largest continents to be considered 'Old World'
		#but leave second largest for new world if wanted
		del continentList[0]
		oldWorldCount -= 1
		newWorldA = None
		if len(continentList) > 0 and isBigNewWorld:
			newWorldA = continentList[0]
			del continentList[0]
		
		while len(continentList) > 0 and oldWorldCount > 0:
			del continentList[0]
			oldWorldCount -= 1
			
		#replace reserved newWorld conti
		if newWorldA != None:
			continentList.append(newWorldA)

		#what remains in the list will be considered 'New World'
		print ''
		print "New World Continents"
		print self.PrintList(continentList)
		
		#if list is empty we need to make a hasty exit
		if len(continentList) == 0:
			return -1
		
		#get ID for the next continent, we will use this ID for 'New World'
		#designation
		nID = continentList[0].ID
		del continentList[0] #delete to avoid unnecessary overwrite

		#now change all the remaining continents to also have nID as their ID
		for i in range(self.mapHeight*self.mapWidth):
			for c in continentList:
				if c.ID == self.areaMap[i]:
					self.areaMap[i] = nID
 		#self.PrintAreaMap()
		return nID
			
	def getIndex(self,x,y):
		#wrap in X direction only.  
		dx = x
		if y >= self.mapHeight or y < 0:
			return -1
		
		if x >= self.mapWidth:
			dx = x % self.mapWidth
		elif x < 0:
			dx = x % self.mapWidth
			
		index = y*self.mapWidth + dx
		return index
	
	def fillArea(self,index,areaID,coastIsLand):
		#first divide index into x and y
		y = index/self.mapWidth
		x = index%self.mapWidth
		#We check 8 neigbors for land,but 4 for water. This is because
		#the game connects land squares diagonally across water, but
		#water squares are not passable diagonally across land
		self.segStack = list()
		self.size = 0
		isAreaWater = self.isWater(x,y,coastIsLand)
		#place seed on stack for both directions
		seg = LineSegment(y,x,x,1)
		self.segStack.append(seg) 
		seg = LineSegment(y+1,x,x,-1)
		self.segStack.append(seg) 
		while(len(self.segStack) > 0):
			seg = self.segStack.pop()
			self.scanAndFillLine(seg,areaID,isAreaWater,coastIsLand)
		
		return self.size,self.isWater(x,y,coastIsLand)
	def scanAndFillLine(self,seg,areaID,isWater,coastIsLand):
		#check for y + dy being off map
		i = self.getIndex(seg.xLeft,seg.y + seg.dy)
		if i < 0:
##			print "scanLine off map ignoring",str(seg)
			return
		debugReport = False
##		if (seg.y < 8 and seg.y > 4) or (seg.y < 70 and seg.y > 64):
##		if (areaID == 4):
##			debugReport = True
		#for land tiles we must look one past the x extents to include
		#8-connected neighbors
		if isWater:
			landOffset = 0
		else:
			landOffset = 1
		lineFound = False
		#first scan and fill any left overhang
		if debugReport:
			print ""
			print "areaID = %(a)4d" % {"a":areaID}
			print "isWater = %(w)2d, landOffset = %(l)2d" % {"w":isWater,"l":landOffset} 
			print str(seg)
			print "Going left"
		for xLeftExtreme in range(seg.xLeft - landOffset,0 - (self.mapWidth*20),-1):
			i = self.getIndex(xLeftExtreme,seg.y + seg.dy)
			if debugReport:
				print "xLeftExtreme = %(xl)4d" % {'xl':xLeftExtreme}
			if self.areaMap[i] == 0 and isWater == self.isWater(xLeftExtreme,seg.y + seg.dy,coastIsLand):
				self.areaMap[i] = areaID
				self.size += 1
				lineFound = True
			else:
				#if no line was found, then xLeftExtreme is fine, but if
				#a line was found going left, then we need to increment
				#xLeftExtreme to represent the inclusive end of the line
				if lineFound:
					xLeftExtreme += 1
				break
		if debugReport:
			print "xLeftExtreme finally = %(xl)4d" % {'xl':xLeftExtreme}
			print "Going Right"
		#now scan right to find extreme right, place each found segment on stack
#		xRightExtreme = seg.xLeft - landOffset #needed sometimes? one time it was not initialized before use.
		xRightExtreme = seg.xLeft #needed sometimes? one time it was not initialized before use.
		for xRightExtreme in range(seg.xLeft,self.mapWidth*20,1):
			if debugReport:			
				print "xRightExtreme = %(xr)4d" % {'xr':xRightExtreme}
			i = self.getIndex(xRightExtreme,seg.y + seg.dy)
			if self.areaMap[i] == 0 and isWater == self.isWater(xRightExtreme,seg.y + seg.dy,coastIsLand):
				self.areaMap[i] = areaID
				self.size += 1
				if lineFound == False:
					lineFound = True
					xLeftExtreme = xRightExtreme #starting new line
					if debugReport:
						print "starting new line at xLeftExtreme= %(xl)4d" % {'xl':xLeftExtreme}
			elif lineFound == True: #found the right end of a line segment!				
				lineFound = False
				#put same direction on stack
				newSeg = LineSegment(seg.y + seg.dy,xLeftExtreme,xRightExtreme - 1,seg.dy)
				self.segStack.append(newSeg)
				if debugReport:
					print "same direction to stack",str(newSeg)
				#determine if we must put reverse direction on stack
				if xLeftExtreme < seg.xLeft or xRightExtreme >= seg.xRight:
					#out of shadow so put reverse direction on stack also
					newSeg = LineSegment(seg.y + seg.dy,xLeftExtreme,xRightExtreme - 1,-seg.dy)
					self.segStack.append(newSeg)
					if debugReport:
						print "opposite direction to stack",str(newSeg)
				if xRightExtreme >= seg.xRight + landOffset:
					if debugReport:
						print "finished with line"
					break; #past the end of the parent line and this line ends
			elif lineFound == False and xRightExtreme >= seg.xRight + landOffset:
				if debugReport:
					print "no additional lines found"
				break; #past the end of the parent line and no line found
			else:
				continue #keep looking for more line segments
		if lineFound == True: #still a line needing to be put on stack
			if debugReport:
				print "still needing to stack some segs"
			lineFound = False
			#put same direction on stack
			newSeg = LineSegment(seg.y + seg.dy,xLeftExtreme,xRightExtreme - 1,seg.dy)
			self.segStack.append(newSeg)
			if debugReport:
				print str(newSeg)
			#determine if we must put reverse direction on stack
			if xLeftExtreme < seg.xLeft or xRightExtreme - 1 > seg.xRight:
				#out of shadow so put reverse direction on stack also
				newSeg = LineSegment(seg.y + seg.dy,xLeftExtreme,xRightExtreme - 1,-seg.dy)
				self.segStack.append(newSeg)
				if debugReport:
					print str(newSeg)
		
		return
		
	#for debugging
	def PrintAreaMap(self):
		
		print "Area Map"
		for y in range(self.mapHeight - 1,-1,-1):
			lineString = ""
			for x in range(self.mapWidth):
				mapLoc = self.areaMap[self.getIndex(x,y)]
				if mapLoc + 34 > 127:
					mapLoc = 127 - 34
				lineString += chr(mapLoc + 34)
			lineString += "-" + str(y)
			print lineString
		oid = self.getOceanID()
		if oid == None or oid + 34 > 255:
			print "Ocean ID is unknown"
		else:
			print "Ocean ID is %(oid)4d or %(c)s" % {'oid':oid,'c':chr(oid + 34)}
		lineString = " "
		print lineString

		return
	def PrintList(self,s):
		for a in s:
			char = chr(a.ID + 34)
			lineString = str(a) + ' ' + char
			print lineString
		
class LineSegment :
	def __init__(self,y,xLeft,xRight,dy):
		self.y = y
		self.xLeft = xLeft
		self.xRight = xRight
		self.dy = dy
	def __str__ (self):
		string = "y = %(y)3d, xLeft = %(xl)3d, xRight = %(xr)3d, dy = %(dy)2d" % \
		{'y':self.y,'xl':self.xLeft,'xr':self.xRight,'dy':self.dy}
		return string
					   
class Area :
	def __init__(self,iD,size,water):
		self.ID = iD
		self.size = size
		self.water = water

	def __str__(self):
		string = "{ID = %(i)4d, size = %(s)4d, water = %(w)1d}" % \
		{'i':self.ID,'s':self.size,'w':self.water}
		return string