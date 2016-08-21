import pymssql


SERVER = 'inetscada.database.windows.net'
USER = 'smartadmin@inetscada'
PASS = 'workshopG2012'
DB = 'inetscada'

class MssqlMapper:
    def __init__(self):
        self.conn = pymssql.connect(server=SERVER, user=USER, password=PASS,
                                    database=DB)
        self.c = self.conn.cursor()

    def get_active_alarm(self, project_id):
        """
        Return a list of active alarms from specified project.
        """
        query = "SELECT id,Description,Class FROM AlarmState" \
                " WHERE ProjectId='%s' AND State='True'" % (project_id)
        self.c.execute(query)

        data = list()

        # when select all fields, row consists of 5 fields:
        # (alarm_id, project_id, state, description, class)
        # ex: (u'GEN01\\CYL_EXH_TMP_001_HI', u'HSD_NPN0', False, 
        #      u'GENERATOR 1 CYLINDER 1 DELTA TEMP.HIGH', 1)

        # fetchall only takes 2 information, please look at query
        for row in self.c.fetchall():
            if row[2] == 0:
                cls = 'Information/Event'
            elif row[2] == 1:
                cls = 'Critical/Error'
            else:
                cls = '#NA'

            r = {
                'class': cls,
                'deviceTagname': row[0],
                'description': row[1]
            }
            data.append(r)
        return data

    def get_alarm_history(self, project_id, start, rows):
        """
        Return a list of alarms history from specified project.
        """
        query = "SELECT AlarmHistorical.Timestamp,AlarmState.Class,AlarmHistorical.AlarmId,AlarmState.Description FROM AlarmHistorical INNER JOIN AlarmState ON AlarmHistorical.Alarmid=AlarmState.id AND AlarmState.ProjectId='%s' ORDER BY AlarmHistorical.Timestamp DESC OFFSET %d ROWS FETCH NEXT %d ROWS ONLY" % (project_id, start, rows)
        self.c.execute(query)

        data = list()
        for row in self.c.fetchall():
            if row[1] == 0:
                cls = 'Information/Event'
            elif row[1] == 1:
                cls = 'Critical/Error'
            else:
                cls = '#NA'

            r = {
                'timestamp': row[0].strftime('%Y-%m-%d %H:%M:%S'),
                'class': cls,
                'deviceTagname': row[2],
                'description': row[3]
            }
            data.append(r)
        return data
