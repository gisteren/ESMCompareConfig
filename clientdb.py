import logging
import sqlite3
import os.path
import os
from subprocess import call

class ClientDb():
    def __init__(self):
        self.checkDBExists()



    def checkDBExists(self):
        logger = logging.getLogger('ESMConfigCompareScript')
        if not os.path.isfile("client.db"):
            try:
                conn = sqlite3.connect('client.db')
                c = conn.cursor()
                logger.info("*****  No SQLite DB found.  Creating new database file.  *****")
                c.execute("CREATE TABLE 'tblESMInstance' ( 'InstanceId' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 'InstanceName' TEXT, 'Type' TEXT DEFAULT 'Live', 'Date'	INTEGER, 'Active' INTEGER UNIQUE, 'URIPrefixRegex'	TEXT);")
                c.execute("CREATE TABLE 'tblImportList' ( 'ImportId' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 'ImportDate' INTEGER, 'InstanceId' INTEGER);")
                c.execute("CREATE TABLE 'tblResource' ( 'tblResourceId' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,	'ResourceName' TEXT,	'ResourceElementName' TEXT, 'ImportId' INTEGER, 'InstanceId' INTEGER, 'ResourceResId'	TEXT, 'ResourceVersionId' TEXT, 'ResourceAction' TEXT, 'ResourceDescription' TEXT);")
                c.execute("CREATE TABLE 'tblResourceChildOf' (	'ChildOfId'	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,	'ImportId'	INTEGER, 'InstanceId' INTEGER, 'ResourceId'	TEXT, 'ChildOfType' TEXT, 'ChildOfURI' TEXT, 'ChildOfResId' TEXT);")
                c.execute("CREATE TABLE 'tblResourceDefinition' ( 'ResourceDefId' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,	'ImportId' INTEGER, 'InstanceId' INTEGER, 'ResourceId'	TEXT, 'ResourceDefFile' TEXT);")
                c.execute("CREATE TABLE 'tblResourceDependant' ( 'ResourceDependantId' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 'ImportId' INTEGER, 'InstanceId' INTEGER, 'ResourceId'	TEXT, 'DependantType' TEXT, 'DependantURI' TEXT, 'DependantResId'	TEXT);")
                c.execute("CREATE TABLE 'tblDependantOf' (	'DependantOfId'	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,	'ImportId'	INTEGER, 'InstanceId' INTEGER, 'ResourceId'	TEXT, 'DependantOfType' TEXT, 'DependantOfResId'	TEXT, 'DependantOfURI' TEXT);")
                c.execute("CREATE TABLE 'tblDefAggregation' (	'DefAggrId'	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,	'ImportId'	INTEGER, 'InstanceId' INTEGER, 'ResourceId'	TEXT, 'TableAlias' TEXT, 'ColumnName'	TEXT);")
                c.execute("CREATE TABLE 'tblDefConditions' (	'DefCondId'	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,	'ImportId'	INTEGER, 'InstanceId' INTEGER, 'ResourceId'	TEXT, 'Condition' TEXT);")
                c.execute("CREATE TABLE 'tblAction' (	'ActionId'	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,	'ImportId'	INTEGER, 'InstanceId' INTEGER, 'ResourceId'	TEXT, 'ActionName' TEXT, 'ActionEvent' TEXT);")
                c.execute("CREATE TABLE 'tblActionParameters' (	'ActionParmId'	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,	'ImportId'	INTEGER, 'InstanceId' INTEGER, 'ResourceId'	TEXT,  'ActionId' INTEGER, 'ActionParmName' TEXT, 'ActionParmValue' TEXT, 'ActionParmResId' TEXT, 'ActionParmURI' TEXT, 'ActionParmRefId' TEXT);")
                c.execute("CREATE TABLE 'tblVariable' (	'VariableId'	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,	'ImportId'	INTEGER, 'InstanceId' INTEGER, 'ResourceId'	TEXT,  'FunctionName' TEXT, 'FieldName' TEXT, 'FieldDisplayNae' TEXT);")
                logger.info("*****  Created DB file  *****")
                c.execute("INSERT INTO 'tblESMInstance'('InstanceName','Date') VALUES ('STAGING','1446441953.65');")
                c.execute("INSERT INTO 'tblESMInstance'('InstanceName','Date') VALUES ('TOP','1446441953.65');")
                c.execute("INSERT INTO 'tblESMInstance'('InstanceName','Date') VALUES ('OS','1446441953.65');")
                c.execute("INSERT INTO 'tblESMInstance'('InstanceName','Date') VALUES ('NETWORK','1446441953.65');")
                c.execute("INSERT INTO 'tblESMInstance'('InstanceName','Date') VALUES ('MID','1446441953.65');")
                c.execute("INSERT INTO 'tblESMInstance'('InstanceName','Date') VALUES ('PROD','1446441953.65');")
                logger.info("*****  Created Base ESM Instances in Database  *****")

                conn.commit()
                conn.close()
            except:
                logger.info("Error Creating database")
        else:
            logger.info("Database exists...")
        return "OK"

    def ping(self):
        return "pong"

    def LookupESMInstanceID(self, InstanceName):
        conn = sqlite3.connect('client.db')
        c = conn.cursor()
        ProcDL = c.execute("select InstanceId from tblESMInstance where InstanceName = '" + InstanceName + "'")
        DownloadList = ProcDL.fetchall()
        for row in DownloadList:
            return row[0]

    def LookupImportID(self):
        conn = sqlite3.connect('client.db')
        c = conn.cursor()
        ProcDL = c.execute("select ImportId from tblImportList order by ImportId DESC ")
        DownloadList = ProcDL.fetchall()
        for row in DownloadList:
            return row[0]

    def insertImportList(self, instanceid):
        from datetime import datetime

        epoch = datetime(1970,1,1)
        i = datetime.now()

        delta_time = (i - epoch).total_seconds()
        conn = sqlite3.connect('client.db')
        c = conn.cursor()
        c.execute("INSERT INTO 'tblImportList'('ImportDate', 'InstanceId') VALUES (" + str(delta_time) + ", " + str(instanceid) + ");")
        conn.commit()
        conn.close()

    def insertResource(self, vcon, ResourceName, ResourceElementName, ImportId, InstanceId, ResResId, ResAction, ResourceDescription):
        c =vcon
        c.execute("INSERT INTO 'tblResource'('ResourceName', 'ResourceElementName', 'ImportId', 'InstanceId', 'ResourceResId','ResourceAction', 'ResourceDescription') VALUES ('" + ResourceName.replace("'", "''") + "', '" + ResourceElementName + "', " + str(ImportId) + ", " + str(InstanceId) + ", '" + str(ResResId) + "', '" + ResAction + "', '" + ResourceDescription.replace("'", "") + "')")

    def insertChildOf(self, ccCon, ImportId, InstanceId, ResourceId, ChildOfType, ChildOfURI, ChildOfResId):
        c = ccCon
        c.execute("INSERT INTO 'tblResourceChildOf'('ImportId','InstanceId','ResourceId','ChildOfType','ChildOfURI','ChildOfResId') VALUES (" + str(ImportId) + ", " + str(InstanceId) + ", '" + str(ResourceId) + "','" + ChildOfType + "','" + ChildOfURI + "','" + ChildOfResId + "')")

    def insertResourceDef(self, vcon, ImportId, InstanceId, ResourceId, ResourceDef):
        # ResDef = os.path.dirname(os.path.abspath(__file__)) + "/download/" + ReourceResId.txt
        c = vcon
        c.execute("INSERT INTO 'tblResourceDefinition'('ImportId','InstanceId','ResourceId','ResourceDefFile') VALUES (" + str(ImportId) + ", " + str(InstanceId) + ", '" + str(ResourceId) + "', '" + ResourceDef.replace('&amp;', '&').replace('&l t;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', '"') + "');")

    def insertRuleAggregationDef(self, vcon, ImportId, InstanceId, ResourceId, TableAlias, ColumnName):
        # ResDef = os.path.dirname(os.path.abspath(__file__)) + "/download/" + ReourceResId.txt
        c = vcon
        c.execute("INSERT INTO 'tblDefAggregation'('ImportId','InstanceId','ResourceId','TableAlias','ColumnName') VALUES (" + str(ImportId) + ", " + str(InstanceId) + ", '" + str(ResourceId) + "', '" + TableAlias + "', '" + ColumnName + "')")

    def insertRuleConditionDef(self, vcon, ImportId, InstanceId, ResourceId, Condition):
        # ResDef = os.path.dirname(os.path.abspath(__file__)) + "/download/" + ReourceResId.txt
        c = vcon
        c.execute("INSERT INTO 'tblDefConditions'('ImportId','InstanceId','ResourceId','Condition') VALUES (" + str(ImportId) + ", " + str(InstanceId) + ", '" + str(ResourceId) + "', '" + Condition.replace("'", "") + "')")

    def insertRuleActionDef(self, vcon, ImportId, InstanceId, ResourceId, ActionName, ActionEvent):
        # ResDef = os.path.dirname(os.path.abspath(__file__)) + "/download/" + ReourceResId.txt
        c = vcon
        c.execute("INSERT INTO 'tblAction'('ImportId','InstanceId','ResourceId','ActionName','ActionEvent') VALUES (" + str(ImportId) + ", " + str(InstanceId) + ", '" + str(ResourceId) + "', '" + ActionName.replace("'", "") + "', '" + ActionEvent.replace("'", "") + "')")

    def LookupActionId(self, vconn):
        c = vconn
        ProcDL = c.execute("select ActionId from tblAction order by ActionId DESC ")
        DownloadList = ProcDL.fetchall()
        for row in DownloadList:
            return row[0]

    def insertRuleActionParmDef(self, vcon, ImportId, InstanceId, ResourceId, ActionId, ActionParmName, ActionParmValue, ActionParmType):
        # ResDef = os.path.dirname(os.path.abspath(__file__)) + "/download/" + ReourceResId.txt
        c = vcon
        c.execute("INSERT INTO 'tblActionParameters'('ImportId','InstanceId','ResourceId','ActionId','ActionParmName','ActionParmValue','ActionParmRefId') VALUES (" + str(ImportId) + ", " + str(InstanceId) + ", '" + str(ResourceId) + "', " + str(ActionId) + ",'" + ActionParmName.replace("'", "") + "','" + ActionParmValue.replace("'", "") + "','" + ActionParmType.replace("'", "") + "')")

    def insertVariables(self, vcon, ImportId, InstanceId, ResourceId, FunctionName, FieldName, FieldDisplayNae):
        # ResDef = os.path.dirname(os.path.abspath(__file__)) + "/download/" + ReourceResId.txt
        c = vcon
        c.execute("INSERT INTO 'tblVariable'('ImportId', 'InstanceId', 'ResourceId', 'FunctionName', 'FieldName', 'FieldDisplayNae') VALUES (" + str(ImportId) + ", " + str(InstanceId) + ", '" + str(ResourceId) + "', '" + str(FunctionName) + "','" + FieldName + "','" +FieldDisplayNae + "')")


