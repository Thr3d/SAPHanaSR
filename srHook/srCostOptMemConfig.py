#!/usr/bin/env python2
"""
"""
#
# parameter section
#
std_userkey = "saphanasr_<sid>_costopt"
version = "20210615-1448"
#
# prepared SQL statements to remove memory allocation limit and pre-load of column tables
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
        else:
            userkey=std_userkey.replace("<sid>", mysid)
        self.tracer.info("version '%s' userkey '%s' sid '%s'" % ( version, userkey, mysid ))

    def about(self):
        return {"provider_company" : "<customer>",
            "provider_name" : "srCostOptMemConfig", # provider name = class name
            "provider_description" : "postTakeover script to reset parameters to default or set parameters as defined in global.ini.",
            "provider_version" : "1.0"}

    def postTakeover(self, rc, **kwargs):
        """Post takeover hook."""
        self.tracer.info("%s.postTakeover method called with rc=%s" % (self.__class__.__name__, rc))
        costopt_primary_global_allocation_limit = 0
        if self.config.hasKey("userkey"):
            userkey=self.config.get("userkey")
        else:
            userkey=std_userkey.replace("<sid>", mysid)
        if self.config.hasKey("costopt_primary_global_allocation_limit"):
            #
            # parameter costopt_primary_global_allocation_limit is set so adjust global_allocation_limit to the defined value
            #
            costopt_primary_global_allocation_limit = self.config.get("costopt_primary_global_allocation_limit")
            sql_set_memory = "ALTER SYSTEM ALTER CONFIGURATION ('global.ini','SYSTEM') SET ('memorymanager','global_allocation_limit') = '%s' WITH RECONFIGURE" % ( costopt_primary_global_allocation_limit )
        else:
            #
            # parameter costopt_primary_global_allocation_limit is NOT set so just unset global_allocation_limit
            #
            sql_set_memory = "ALTER SYSTEM ALTER CONFIGURATION ('global.ini','SYSTEM') UNSET ('memorymanager','global_allocation_limit') WITH RECONFIGURE"
        self.tracer.info("version '%s' userkey '%s' sid '%s'" % ( version, userkey, mysid ))
        sql_set_preload = "ALTER SYSTEM ALTER CONFIGURATION ('global.ini','SYSTEM') UNSET ('system_replication','preload_column_tables') WITH RECONFIGURE"
        # TODO: PRIO4: Do we need to differ forced (rc=1) and normal (rc=0) takeover?
        if ( rc == 0 or rc == 1 ):
            # normal takeover succeeded
            conn = dbapi.connect(
                       key=userkey,
                       # address='localhost',port=dbport,user=dbuser,passwort=dbpwd,
                   )
            cursor = conn.cursor()
            self.tracer.info("sqlstatement: %s" % (sql_set_memory))
            cursor.execute(sql_set_memory)
            self.tracer.info("sqlstatement: %s" % (sql_set_preload))
            cursor.execute(sql_set_preload)
            return 0
        elif rc == 2:
            # error, something went wrong
            return 0
