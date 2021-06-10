#!/usr/bin/env python2
"""
"""
#
# parameter section
#
userkey = "saphanasr_<sid>_costopt"
version = "20210610-1043"
#
# prepared SQL statements to remove memory allocation limit and pre-load of column tables
#
#
stmnt1 = "ALTER SYSTEM ALTER CONFIGURATION ('global.ini','SYSTEM') UNSET ('memorymanager','global_allocation_limit') WITH RECONFIGURE"
stmnt2 = "ALTER SYSTEM ALTER CONFIGURATION ('global.ini','SYSTEM') UNSET ('system_replication','preload_column_tables') WITH RECONFIGURE"
stmnt3 = "ALTER SYSTEM ALTER CONFIGURATION ('global.ini','SYSTEM') SET ('my_section','my_param', 'my_value') WITH RECONFIGURE"
#
# loading classes and libraries
#
import platform
import os, time
from hdb_ha_dr.client import HADRBase, Helper
from hdbcli import dbapi
#
mySID = os.environ.get('SAPSYSTEMNAME')
mysid = mySID.lower()
#
# class definition srCostOptMemConfig
#
class srCostOptMemConfig(HADRBase):
    def __init__(self, *args, **kwargs):
        # delegate construction to base class
        super(srCostOptMemConfig, self).__init__(*args, **kwargs)
        if self.config.hasKey("userkey"):
            userkey=self.config.get("userkey")
        self.tracer.info("version '%s' userkey '%s' sid '%s'" % ( version, userkey, mysid ))

    def about(self):
        return {"provider_company" : "<customer>",
            "provider_name" : "srCostOptMemConfig", # provider name = class name
            "provider_description" : "Replication takeover script to set parameters to default.",
            "provider_version" : "1.0"}

    def srServiceStateChanged(self, parameters, **kwargs):
        self.tracer.info("enter srServiceStateChanged hook; %s" % locals())
        service = parameters['service_name']
        conn = dbapi.connect(
                   key=userkey,
                   # address='localhost',port=dbport,user=dbuser,passwort=dbpwd,
               )
        cursor = conn.cursor()
        sqlstmnt = "ALTER SYSTEM ALTER CONFIGURATION ('global.ini','SYSTEM') SET ('my_section','my_param', '%s') WITH RECONFIGURE" % (service)
        self.tracer.info("sqlstatement: %s" % (sqlstmnt))
        cursor.execute(sqlstmnt)
        return 0
        

    def postTakeover(self, rc, **kwargs):
        """Post takeover hook."""
        self.tracer.info("%s.postTakeover method called with rc=%s" % (self.__class__.__name__, rc))
        # TODO: PRIO4: Do we need to differ forced (rc=1) and normal (rc=0) takeover?
        if ( rc == 0 or rc == 1 ):
            # normal takeover succeeded
            conn = dbapi.connect(
                       key=userkey,
                       # address='localhost',port=dbport,user=dbuser,passwort=dbpwd,
                   )
            cursor = conn.cursor()
            cursor.execute(stmnt1)
            cursor.execute(stmnt2)
            return 0
        elif rc == 2:
            # error, something went wrong
            return 0
