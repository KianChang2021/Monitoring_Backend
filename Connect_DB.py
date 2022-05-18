import pyodbc 

conn = pyodbc.connect('')

def get_branch():
    cursor = conn.cursor()
    cursor.execute('''
         SELECT [BranchName] FROM [RIMSDB_CONCENTRATOR].[ssp].[tbl_ConcentratorConfiguration]
    ''')
    data = cursor.fetchall()
    cursor.close()
    return data

def get_Station():
    cursor = conn.cursor()
    cursor.execute('''
        SELECT [SerialNumber],[NetworkAddress],[BrandName] FROM [RIMSDB_CONCENTRATOR].[ssp].[tbl_ConcentratorStation]
        union
        SELECT [SerialNumber],[NetworkAddress],[BrandName] FROM [RIMSDB_CONCENTRATOR].[ssp].[tbl_ConcentratorStation_AK98V2]
    ''')
    data = cursor.fetchall()
    
    cursor.close()
    return data

def machine_assigned():
    cursor = conn.cursor()
    cursor.execute('''
         SELECT top 1 [SerialNumber],[PatientName],[DialysisDate] FROM [RIMSDB_CONCENTRATOR].[ssp].[tbl_MachinePatientMapping] where cast(DialysisDate as Date) = cast(getdate() as Date) order by DialysisDate DESC
    ''')
    data = cursor.fetchall()
    cursor.close()
    return data

def first_data_machine():
    cursor = conn.cursor()
    cursor.execute('''
         SELECT top 1 [SerialNumber],[PatientName],[DialysisDate] FROM [RIMSDB_CONCENTRATOR].[ssp].[tbl_MachinePatientMapping] where cast(DialysisDate as Date) = cast(getdate() as Date) order by DialysisDate DESC
    ''')
    data = cursor.fetchall()
    cursor.close()
    return data



def machine_assigned_status(serial_number):
    cursor = conn.cursor()
    cursor.execute('''
         SELECT top 1 [SerialNumber],[BrandName],[PatientName],[DialysisDate] FROM [RIMSDB_CONCENTRATOR].[ssp].[tbl_MachinePatientMapping] where SerialNumber = '{0}' and cast(DialysisDate as Date) = cast(getdate() as Date) order by DialysisDate DESC
    '''.format(serial_number))
    data = cursor.fetchall()
    cursor.close()
    return data

def get_last_Gambro_last_sync_data(serial_number,patient_name):
    cursor = conn.cursor()
    cursor.execute('''
         SELECT TOP 1 * FROM [RIMSDB_CONCENTRATOR].[dis].[tbl_GambroReadings] where DialogSerialNumber = '{0}' and PatientName = '{1}' and UploadStatus = 1 order by CreatedTime desc
    '''.format(serial_number,patient_name))
    data = cursor.fetchall()
    cursor.close()
    return data

def get_last_BBraun_last_sync_data(serial_number,patient_name):
    cursor = conn.cursor()
    cursor.execute('''
         SELECT TOP 1 * FROM [RIMSDB_CONCENTRATOR].[dis].[tbl_BBraunReadings] where DialogSerialNumber = '{0}' and PatientName = '{1}' and UploadStatus = 1 order by CreatedTime desc
    '''.format(serial_number,patient_name))
    data = cursor.fetchall()
    cursor.close()
    return data

def get_last_Gambro_data_HD_Machine(x):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT TOP 1 * FROM [RIMSDB_CONCENTRATOR].[dis].[tbl_GambroReadings] where DialogSerialNumber = '{0}' and cast(CreatedTime as Date) = cast(getdate() as Date) order by CreatedTime desc
    '''.format(x))
    data = cursor.fetchall()
    cursor.close()
    return data

def get_last_BBraun_data_HD_Machine(x):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT TOP 1 * FROM [RIMSDB_CONCENTRATOR].[dis].[tbl_BBraunReadings] where DialogSerialNumber = '{0}' and cast(CreatedTime as Date) = cast(getdate() as Date) order by CreatedTime desc
    '''.format(x))
    data = cursor.fetchall()
    cursor.close()
    return data

def get_station_ip(x):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT [NetworkAddress] FROM [RIMSDB_CONCENTRATOR].[ssp].[tbl_ConcentratorStation]
        where SerialNumber = '{0}'
        union
        SELECT [NetworkAddress] FROM [RIMSDB_CONCENTRATOR].[ssp].[tbl_ConcentratorStation_AK98V2]
        where SerialNumber = '{0}'
    '''.format(str(x)))
    data = cursor.fetchall()
    cursor.close()
    return data

def check_end_or_not_gambro(x,patient_name):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT TOP 1 * FROM [RIMSDB_CONCENTRATOR].[dis].[tbl_GambroReadings] where DialogSerialNumber = '{0}' and PatientName='{1}' and  MainPhase = 3 and cast(CreatedTime as Date) = cast(getdate() as Date) order by CreatedTime desc
    '''.format(int(x),patient_name))
    data = cursor.fetchall()
    cursor.close()
    return data

def check_end_or_not_bbraun(x,patient_name):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT TOP 1 * FROM [RIMSDB_CONCENTRATOR].[dis].[tbl_BBraunReadings] where DialogSerialNumber = {0} and PatientName='{1}'and MainPhase = 3 and cast(CreatedTime as Date) = cast(getdate() as Date) order by CreatedTime desc
    '''.format(int(x),patient_name))
    data = cursor.fetchall()
    cursor.close()
    return data

if __name__ == "__main__":
    aa = get_branch()