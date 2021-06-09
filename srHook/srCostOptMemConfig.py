#!/usr/bin/env python2
"""
Sample for a HA/DR hook provider for method srPostTakeover().
When using your own code in here, please copy this file to location on /hana/shared
outside the HANA installation.
To configure your own changed version of this file, please add to your global.ini lines
similar to this:
[ha_dr_provider_<className>]
provider = <className>
path = /hana/shared/srHook/
execution_order = 2
For all hooks, 0 must be returned in case of success.
Set the following variables:
* dbinst Instance Number [e.g. 00 - 99 ]
* dbuser Username [ e.g. SYSTEM ]
* dbpwd
* user password [ e.g. SLES4sap ]
* dbport port where db listens for SQL connctions [e.g 30013 or 30015]
"""
#
# parameter section
#
#
# prepared SQL statements to remove memory allocation limit and pre-load of column tables
#
#
stmnt1 = "ALTER SYSTEM ALTER CONFIGURATION ('global.ini','SYSTEM') UNSET ('memorymanager','global_allocation_limit') WITH RECONFIGURE"
stmnt2 = "ALTER SYSTEM ALTER CONFIGURATION ('global.ini','SYSTEM') UNSET ('system_replication','preload_column_tables') WITH RECONFIGURE"
#
# loading classes and libraries
#
import platform
import os, time
from hdb_ha_dr.client import HADRBase, Helper
from hdbcli import dbapi
#
# class definition srCostOptMemConfig
#
class srCostOptMemConfig(HADRBase):
    def __init__(self, *args, **kwargs):
        # delegate construction to base class
        super(srCostOptMemConfig, self).__init__(*args, **kwargs)

    def about(self):
        return {"provider_company" : "<customer>",
            "provider_name" : "srCostOptMemConfig", # provider name = class name
            "provider_description" : "Replication takeover script to set parameters to default.",
            "provider_version" : "1.0"}

    def postTakeover(self, rc, **kwargs):
        """Post takeover hook."""
        self.tracer.info("%s.postTakeover method called with rc=%s" % (self.__class__.__name__, rc))
        if rc == 0:
            # normal takeover succeeded
            conn = dbapi.connect('localhost',dbport,dbuser,dbpwd)
            cursor = conn.cursor()
            cursor.execute(stmnt1)
            cursor.execute(stmnt2)
            return 0
        elif rc == 1:
            # waiting for force takeover
            conn = dbapi.connect('localhost',dbport,dbuser,dbpwd)
            cursor = conn.cursor()
            cursor.execute(stmnt1)
            cursor.execute(stmnt2)
            return 0
        elif rc == 2:
            # error, something went wrong
            return 0
