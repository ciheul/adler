import pymssql


SERVER = 'inetscada.database.windows.net'
USER = 'smartadmin'
PASS = 'workshopG2012'
DB = 'inetscada'

class MssqlMapper:
    def __init__(self):
        self.conn = pymssql.connect(server=SERVER, user=USER, password=PASS,
                                    database=DB)
        self.c = self.conn.cursor()

    def get_active_alarms(self, project_id):
        """
        Return a list of active alarms from specified project.
        """
        query = "SELECT id,Description FROM AlarmState" \
                " WHERE ProjectId=%s AND State='True'" % (project_id)
        self.c.execute(query)

        data = list()

        # when select all fields, row consists of 5 fields:
        # (alarm_id, project_id, state, description, class)
        # ex: (u'GEN01\\CYL_EXH_TMP_001_HI', u'HSD_NPN0', False, 
        #      u'GENERATOR 1 CYLINDER 1 DELTA TEMP.HIGH', 1)

        # fetchall only takes 2 information, please look at query
        for row in self.c.fetchall():
            r = { 'class': 'Alarm', 'alarm_id': row[0], 'description': row[1] }
            data.append(r)
        return data
