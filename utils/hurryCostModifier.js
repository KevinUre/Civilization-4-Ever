const fs = require('fs')
const path = require('path');
var parser = require('fast-xml-parser');

const eraOrder = {
    NONE: 0,
    ERA_ANCIENT: 1,
    ERA_CLASSICAL: 2,
    ERA_MEDIEVAL: 3,
    ERA_RENAISSANCE: 4,
    ERA_INDUSTRIAL: 5,
    ERA_MODERN: 6,
    ERA_FUTURE: 7
}

const unitCostsPerEra = {
    NONE: 50,
    ERA_ANCIENT: 50,
    ERA_CLASSICAL: 60,
    ERA_MEDIEVAL: 70,
    ERA_RENAISSANCE: 80,
    ERA_INDUSTRIAL: 90,
    ERA_MODERN: 100,
    ERA_FUTURE: 100
}
const ignoredUnitClasses = [
    'UNITCLASS_SETTLER',
    'UNITCLASS_WORKER',
]
const buildingCostsPerEra = {
    NONE: 25,
    ERA_ANCIENT: 25,
    ERA_CLASSICAL: 30,
    ERA_MEDIEVAL: 35,
    ERA_RENAISSANCE: 40,
    ERA_INDUSTRIAL: 45,
    ERA_MODERN: 50,
    ERA_FUTURE: 50
}
const ignoredBuildingHurryCosts = [0,200]


function getTechs() {
    const pathToTechXml = path.join(__dirname, '../', './mod-components/Assets/XML/', 'Technologies/CIV4TechInfos.xml')
    const xmlData = fs.readFileSync(pathToTechXml).toString();
    const jsObj = parser.parse(xmlData);
    return jsObj;
}

function getUnits() {
    const pathToTechXml = path.join(__dirname, '../', './mod-components/Assets/XML/', 'Units/CIV4UnitInfos.xml')
    const xmlData = fs.readFileSync(pathToTechXml).toString();
    const jsObj = parser.parse(xmlData);
    return jsObj;
}

function getBuildings() {
    const pathToTechXml = path.join(__dirname, '../', './mod-components/Assets/XML/', 'Buildings/CIV4BuildingInfos.xml')
    const xmlData = fs.readFileSync(pathToTechXml).toString();
    const jsObj = parser.parse(xmlData);
    return jsObj;
}

const techs = getTechs();

function getEraFromTech(tech) {
    const element = techs.Civ4TechInfos.TechInfos.TechInfo.find(e => e.Type == tech);
    return element.Era;
}

function getUnitEra(unit) {
    if (unit.PrereqTech === 'NONE') { return 'NONE';}
    let era = getEraFromTech(unit.PrereqTech);
    if (unit.TechTypes !== '') {
        for(var prereq of unit.TechTypes.PrereqTech) {
            if(prereq !== 'NONE') {
                let tempera = getEraFromTech(prereq);
                if (eraOrder[tempera] > eraOrder[era]) {
                    era = tempera;
                }
            }
        }
    }
    return era;
}

function getBuildingEra(building) {
    if (building.PrereqTech === 'NONE') { return 'NONE';}
    let era = getEraFromTech(building.PrereqTech);
    if (building.TechTypes !== '') {
        for(var prereq of building.TechTypes.PrereqTech) {
            if(prereq !== 'NONE') {
                let tempera = getEraFromTech(prereq);
                if (eraOrder[tempera] > eraOrder[era]) {
                    era = tempera;
                }
            }
        }
    }
    return era;
}

function handleUnit(unit) {
    if(ignoredUnitClasses.includes(unit.Class)) {return unit;}
    const era = getUnitEra(unit);
    unit.iHurryCostModifier = unitCostsPerEra[era];
    return unit;
}

function handleBuilding(building) {
    building.fVisibilityPriority = `${building.fVisibilityPriority}.0` // correct floating point issue
    if(ignoredBuildingHurryCosts.includes(building.iHurryCostModifier)) { return building; }
    const era = getBuildingEra(building);
    building.iHurryCostModifier = buildingCostsPerEra[era];
    return building;
}

let units = getUnits();
let buildings = getBuildings();

for(let i = 0; i < units.Civ4UnitInfos.UnitInfos.UnitInfo.length; i++) {
    units.Civ4UnitInfos.UnitInfos.UnitInfo[i] = handleUnit(units.Civ4UnitInfos.UnitInfos.UnitInfo[i])
}
for(let i = 0; i < buildings.Civ4BuildingInfos.BuildingInfos.BuildingInfo.length; i++) {
    buildings.Civ4BuildingInfos.BuildingInfos.BuildingInfo[i] = handleBuilding(buildings.Civ4BuildingInfos.BuildingInfos.BuildingInfo[i]) 
}

const j2xParser = new parser.j2xParser({format: true, indentBy: '\t'});

const unitRawXml = j2xParser.parse(units);
const unitXml = unitRawXml.replace(/\<(.*?)\>\<\/\1\>/g, '<$1/>') // use self-closing tags for empties
fs.writeFileSync('./units.xml', unitXml);

const buildingRawXml = j2xParser.parse(buildings);
const buildingXml = buildingRawXml.replace(/\<(.*?)\>\<\/\1\>/g, '<$1/>') // use self-closing tags for empties
fs.writeFileSync('./buildings.xml', buildingXml);


