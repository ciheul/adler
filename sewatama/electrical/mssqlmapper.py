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
        query = "SELECT id,Description FROM AlarmState" \
                " WHERE ProjectId='%s' AND State='True'" % (project_id)
        # query = "SELECT id,Description FROM AlarmState"

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

    def get_historical_alarm(self, project_id):
        # take timestamp, alarmId, and description (using relationship)
        # sort by latest timestamp for specified projectId
        query = "SELECT AlarmHistorical.Timestamp,AlarmHistorical.AlarmId, " \
                "       AlarmState.Description " \
                "FROM AlarmHistorical " \
                "INNER JOIN AlarmState " \
                "ON AlarmHistorical.AlarmId=AlarmState.id " \
                "WHERE AlarmState.ProjectId='%s' " \
                "ORDER BY AlarmHistorical.Timestamp DESC" % project_id
        self.c.execute(query)

        data = list()
        for row in self.c.fetchall():
            r = {
                'class': 'Alarm',
                'timestamp': row[0].strftime('%Y-%m-%d %H:%M:%S'),
                'alarm_id': row[1],
                'description': row[2] }
            data.append(r)
        return data
