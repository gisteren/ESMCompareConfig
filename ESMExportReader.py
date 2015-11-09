__author__ = 'Vosteen'
import logging
import ESMConfigCompareCommon
import clientdb
import xml.etree.ElementTree as ET
import sys, re, os
import time, datetime
import shutil

class arcsightXMLParser():

    def __init__(self):
        if not os.path.exists("./payload/"):
            os.mkdir("./payload/")
        root = ""

    def CleanFileofListsNote(self, vfilname):
        DBCon = clientdb.ClientDb()
        try:
            tree = ET.parse(vfilname)
        except:
            sys.exit("Could not open XML file")

        root = tree.getroot()
        ruleinfo = root.findall("./Note")
        for rules in ruleinfo:
            root.remove(rules)

        listinfo = root.findall("./ActiveList")
        for list in listinfo:
            root.remove(list)

        ri = ET.ElementTree(root)
        ri.write(vfilname.replace(".xml", "-modified.xml"))

        return vfilname.replace(".xml", "-modified.xml")

    def ReadChildOf(self, vroot, vccCon, vfilname, ResType, ResourceResId, ImportId, InstanceId):
        import clientdb
        DBCon = clientdb.ClientDb()

        caselist = []
        childOfList = vroot.findall("./" + ResType + "[@id='" + ResourceResId + "']/childOf/list/*")

        for childOf in childOfList:
            DBCon.insertChildOf(vccCon, ImportId, InstanceId, ResourceResId, childOf.attrib['type'], childOf.attrib['uri'], childOf.attrib['id'])

    def ReadResDef(self, vroot, vccCon, ResType, ResourceResId, ImportId, InstanceId):
        import re
        vreg = ".*/Microsoft/IT/.*|.*/Microsoft IT/.*|.*/Microsoft IT Clients and Partners/.*"
        if ResType == "Rule":
            import clientdb
            DBCon = clientdb.ClientDb()
            ResDefList = vroot.findall("./Rule[@id='" + ResourceResId + "']/def")
            for ResDef in ResDefList:
                # DBCon.insertChildOf(vccCon, ImportId, InstanceId, ResourceResId, "Rule", ResDef.attrib['uri'], ResDef.attrib['id'])
                DBCon.insertResourceDef(vccCon, ImportId, InstanceId, ResourceResId, re.sub(vreg, "", ResDef.text.replace('&', '&amp;').replace('<', '&l t;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')))
                arcsightXMLParser.ReadAggregationField(self, vccCon, ImportId, InstanceId, ResourceResId, re.sub(vreg, "", ResDef.text.replace('&amp;','&').replace('&l t;','<').replace('&gt;', '>').replace('&quot;','"').replace('&#39;',"'")), "Aggregation", ResourceResId)
                arcsightXMLParser.ReadConditionField(self, vccCon, ImportId, InstanceId, ResourceResId, re.sub(vreg, "", ResDef.text.replace('&amp;','&').replace('&l t;','<').replace('&gt;', '>').replace('&quot;','"').replace('&#39;',"'")), "Aggregation", ResourceResId)
                arcsightXMLParser.ReadActionField(self, vccCon, ImportId, InstanceId, ResourceResId, re.sub(vreg, "", ResDef.text.replace('&amp;','&').replace('&l t;','<').replace('&gt;', '>').replace('&quot;','"').replace('&#39;',"'")))
                arcsightXMLParser.ReadLocalVariableField(self, vccCon, ImportId, InstanceId, ResourceResId, ResDef.text.replace('&amp;','&').replace('&l t;','<').replace('&gt;', '>').replace('&quot;','"').replace('&#39;',"'"))
        elif ResType == "Filter":
            import clientdb
            DBCon = clientdb.ClientDb()
            ResDefList = vroot.findall("./Filter[@id='" + ResourceResId + "']/definition")
            for ResDef in ResDefList:
                # DBCon.insertChildOf(vccCon, ImportId, InstanceId, ResourceResId, ResDef.attrib['type'], ResDef.attrib['uri'], ResDef.attrib['id'])
                DBCon.insertResourceDef(vccCon, ImportId, InstanceId, ResourceResId, re.sub(vreg, "", ResDef.text.replace('&', '&amp;').replace('<', '&l t;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')))
        elif ResType == "Field":
            import clientdb
            DBCon = clientdb.ClientDb()
            ResDefList = vroot.findall("./Field[@id='" + ResourceResId + "']/variableXML")
            for ResDef in ResDefList:
                # DBCon.insertChildOf(vccCon, ImportId, InstanceId, ResourceResId, ResDef.attrib['type'], ResDef.attrib['uri'], ResDef.attrib['id'])
                DBCon.insertResourceDef(vccCon, ImportId, InstanceId, ResourceResId, re.sub(vreg, "", ResDef.text.replace('&', '&amp;').replace('<', '&l t;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')))

    def ReadResource(self, vroot, vfilname, restype, ImportId, InstanceId):
        import sqlite3
        payloadfolder = "./payload/"
        DBCon = clientdb.ClientDb()

        conn = sqlite3.connect('client.db')
        ccCon = conn.cursor()

        ruleinfo = vroot.findall("./" + restype)
        for rules in ruleinfo:
            uri = ""
            try:
                uri = rules.attrib['uri']
            except:
                uri = "None Found in XML"

            DBCon.insertResource(ccCon, rules.attrib['name'], restype, ImportId, InstanceId, rules.attrib['id'], rules.attrib['action'], uri)
            arcsightXMLParser.ReadChildOf(self, vroot, ccCon, vfilname, restype, rules.attrib['id'], ImportId, InstanceId)
            if restype == "Rule" or restype == "Filter" or restype == "Field":
                arcsightXMLParser.ReadResDef(self, vroot, ccCon, restype, rules.attrib['id'], ImportId, InstanceId)

        conn.commit()
        conn.close()
        return "ok"


    def ReadAggregationField(self, vcon, ImportId, InstanceId, ResourceId, xmldef, ruledef, ResourceResId):
        import xml.etree.ElementTree as ET
        from lxml import etree
        DBCon = clientdb.ClientDb()

        if len(xmldef) > 2:
            parser = etree.XMLParser(recover=True)
            root = ET.fromstring(xmldef, parser=parser)
            # root = tree.getroot()
            ruledefinfo = root.findall("./Query/GroupByClause/*")

            # print ruledefinfo
            for ruledef in ruledefinfo:
                DBCon.insertRuleAggregationDef(vcon, ImportId, InstanceId, ResourceId, ruledef.attrib['TableAlias'], ruledef.attrib['Column'])
        else:
            DBCon.insertRuleAggregationDef(vcon, ImportId, InstanceId, ResourceId, "NO AGGREGATION", "NO AGGREGATION")

        return "ok"

    def ReadConditionField(self, vcon, ImportId, InstanceId, ResourceId, xmldef, ruledef, ResourceResId):
        import xml.etree.ElementTree as ET
        from lxml import etree
        import re
        DBCon = clientdb.ClientDb()
        vreg = ".*(URI=\".*\").*"


        if len(xmldef) > 2:
            parser = etree.XMLParser(recover=True)
            root = ET.fromstring(xmldef, parser=parser)
            # root = tree.getroot()
            ruledefinfo = root.findall("./Query/WhereClause/*")

            # print ruledefinfo
            for ruledef in ruledefinfo:
                DBCon.insertRuleConditionDef(vcon, ImportId, InstanceId, ResourceId, re.sub(vreg, "", ET.tostring(ruledef)))
        else:
            DBCon.insertRuleConditionDef(vcon, ImportId, InstanceId, ResourceId, "NO RULE CONDITIONS-FILTERS")

        return "ok"

    def ReadActionField(self, vcon, ImportId, InstanceId, ResourceId, xmldef):
        import xml.etree.ElementTree as ET
        from lxml import etree
        import re
        DBCon = clientdb.ClientDb()
        vreg = ".*(URI=\".*\").*"

        parser = etree.XMLParser(recover=True)
        root = ET.fromstring(xmldef, parser=parser)
        # root = tree.getroot()
        ruledefinfo = root.findall("./Actions/*")

        # print ruledefinfo
        for ruledef in ruledefinfo:
            actionid = 0
            DBCon.insertRuleActionDef(vcon, ImportId, InstanceId, ResourceId, 'Action', ruledef.attrib['Event'])
            actionid = int(DBCon.LookupActionId(vcon))
            for action in ruledef:
                try:
                    FieldName = action.attrib['EventFieldName']
                    FieldValue = action.attrib['EventFieldValue']
                except:
                    FieldName = ""
                    FieldValue = ""
                DBCon.insertRuleActionParmDef(vcon, ImportId, InstanceId, ResourceId, actionid, FieldName, FieldValue, action.tag)

    def ReadLocalVariableField(self, vcon, ImportId, InstanceId, ResourceId, xmldef):
        import xml.etree.ElementTree as ET
        from lxml import etree
        DBCon = clientdb.ClientDb()

        parser = etree.XMLParser(recover=True)
        root = ET.fromstring(xmldef, parser=parser)
        # root = tree.getroot()
        ruledefinfo = root.findall("./DependentVariables/DependentVariable")

        # print ruledefinfo
        for ruledef in ruledefinfo:
            DBCon.insertVariables(vcon, ImportId, InstanceId, ResourceId, ruledef.attrib['FunctionName'], ruledef.attrib['FieldName'], ruledef.attrib['FieldDisplayName'])
