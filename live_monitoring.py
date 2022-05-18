from datetime import date
from operator import truediv
import Connect_DB,logger,PortService
import datetime,time,logging,calendar
import send_gmail as send
import schedule,psutil,os,requests

Dialysis_Time = datetime.timedelta(4)
branch_data = Connect_DB.get_branch()
branch_name = branch_data[0].BranchName

def service_check():
    try:
        s = requests.Session()
        r = s.get('')
        if r.status_code != 200:
                send.service_issue(branch_name)
    except Exception as ex:
        send.service_issue(branch_name)
        data = "Error Network Monitoring : "+ str(ex)
        logger.main_log(data)
    

def network():
    try:
        url = ""
        payload="{\"branch\":\""+branch_name+"\"}"
        headers = {
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        if 'Success' not in response.text:
            data = "Fail Api in network "+ str(response.status_code)
            logger.main_log(data)

    except Exception as ex:
        data = "Error Network Monitoring : "+ str(ex)
        logger.main_log(data)

def main():
    try:
        list_station = Connect_DB.get_Station()
        data = ""
        for x in list_station:
            if (x.SerialNumber) != "WS1":
                Ma_assigned_patient = Connect_DB.machine_assigned_status(x.SerialNumber)
                
                last_hd_time = ""
                for y in Ma_assigned_patient:
                    end_data = []
                    if y.BrandName == "Gambro":
                        HD_data = Connect_DB.get_last_Gambro_data_HD_Machine(str(y.SerialNumber))
                        data_last_sync = Connect_DB.get_last_Gambro_last_sync_data(str(y.SerialNumber),str(y.PatientName))
                    elif y.BrandName == "BBraun":
                        HD_data = Connect_DB.get_last_BBraun_data_HD_Machine(str(y.SerialNumber))
                        data_last_sync = Connect_DB.get_last_BBraun_last_sync_data(str(y.SerialNumber),str(y.PatientName))
                    else:
                        HD_data = []
                    # Check last sync data if more than 10 minute consider fail
                    if data_last_sync != []:
                        if HD_data != []:
                            for z in HD_data:
                                if z.MainPhase == 2:
                                    
                                    time_now = datetime.datetime.now()
                                    new_data = time_now - data_last_sync[0].CreatedTime
                                    days, hours, minutes = new_data.days, new_data.seconds // 3600, new_data.seconds // 60 % 60
                                    timestamp = datetime.datetime.timestamp(data_last_sync[0].CreatedTime)
                                    data = [str(y.SerialNumber),int(timestamp)]
                                    if days == 0:
                                        if hours>= 0:
                                            if minutes >= 10:
                                                send.late_sync_gmail(str(y.SerialNumber),branch_name)
                                    # Haven decide it can consider bug or not 
                                    # try:
                                    #     url = ""

                                    #     payload="{\"serial_number\":\""+y.SerialNumber+"\",\"timestamp\":"+timestamp+",\"branch\":\""+branch_name+"\"}"
                                    #     headers = {
                                    #     'Content-Type': 'application/json'
                                    #     }
                                    #     response = requests.request("POST", url, headers=headers, data=payload)
                                    #     if 'Success' in response.text:
                                    #         data = "Fail Api HD "+ str(response.status_code)
                                    #         logger.main_log(data)

                                    # except Exception as ex:
                                    #     data = "Error Network Monitoring : "+ str(ex)
                                    #     logger.main_log(data)
                                    

                    # Check HD_data behaviour
                    if HD_data != []:
                        for z in HD_data:
                            last_hd_time = z.CreatedTime
                            time_now = datetime.datetime.now()
                            minute_diff= time_now - last_hd_time
                            if minute_diff> datetime.timedelta(minutes=5):
                                if z.MainPhase <= 2:
                                    try:
                                        
                                        # -- Restart MA --
                                        #=============== AD Only =================
                                        # if str(z.DialogSerialNumber) == "16440":
                                        #     D = Connect_DB.get_station_ip(str(z.DialogSerialNumber))
                                        #     response = os.popen(f"ping "+D[0].NetworkAddress+"").read()
                                        #     if "Received = 4" in response:
                                        #         break
                                        #     else:
                                        #         response = os.popen(f"ping "+D[0].NetworkAddress+"").read()
                                        #         if "Received = 4" in response:
                                        #             break
                                        #         else:
                                        #             PortService.restart_Ma(str(D[0].NetworkAddress))
                                        #             try:
                                        #                 url = ""

                                        #                 payload="{\"serial_number\":\""+str(z.DialogSerialNumber)+"\",\"ip\":\""+D[0].NetworkAddress+"\",\"branch\":\""+branch_name+"\"}"
                                        #                 headers = {
                                        #                 'Content-Type': 'application/json'
                                        #                 }

                                        #                 response = requests.request("POST", url, headers=headers, data=payload)
                                        #                 if 'Success' in response.text: 
                                        #                     data = "Fail Api MA "+ str(response.status_code)
                                        #                     logger.main_log(data)

                                        #             except Exception as ex:
                                        #                 data = "Error Network Monitoring : "+ str(ex)
                                        #                 logger.main_log(data)      
                                        #=============== AD Only =================
                                        # Check assigned Machine Name is tally or not 
                                        
                                        if y.PatientName != z.PatientName:
                                            if z.MainPhase == 2:
                                                timestamp = datetime.datetime.timestamp(z.CreatedTime)
                                                new_timestamp = int(timestamp)
                                                data = [str(z.DialogSerialNumber),int(timestamp)]
                                                try:
                                                    url = ""

                                                    payload="{\"serial_number\":\""+str(z.DialogSerialNumber)+"\",\"timestamp\":"+str(new_timestamp)+",\"branch\":\""+branch_name+"\"}"
                                                    headers = {
                                                    'Content-Type': 'application/json'
                                                    }

                                                    response = requests.request("POST", url, headers=headers, data=payload)

                                                    if 'Success' not in response.text:
                                                        data = "Fail Api HD "+str(y.PatientName)+" "+str(z.PatientName)+str(z.DialogSerialNumber)+ str(response.status_code)
                                                        logger.main_log(data)

                                                except Exception as ex:
                                                    data = "Error Network Monitoring : "+ str(ex)
                                                    logger.main_log(data)
                                                
                                                send.patient_name(str(z.DialogSerialNumber),branch_name)

                                        else:
                                            if y.BrandName == "Gambro":
                                                end_data = Connect_DB.check_end_or_not_gambro(str(y.SerialNumber),str(y.PatientName))
                                                
                                            elif y.BrandName == "BBraun":
                                                end_data = Connect_DB.check_end_or_not_bbraun(str(y.SerialNumber),str(y.PatientName))
                                            
                                            
                                            if end_data == []:
                                                D = Connect_DB.get_station_ip(str(z.DialogSerialNumber))
                                                response = os.popen(f"ping "+D[0].NetworkAddress+"").read()
                                                try:
                                                    if "Lost = 0" in response:
                                                        break
                                                    else:
                                                        response_text = "Network ping issue on station " +str(z.DialogSerialNumber)
                                                        logger.ma_log(response_text)
                                                        
                                                        url = ""

                                                        payload="{\"serial_number\":\""+str(z.DialogSerialNumber)+"\",\"ip\":\""+str(D[0].NetworkAddress)+"\",\"branch\":\""+branch_name+"\"}"
                                                        headers = {
                                                        'Content-Type': 'application/json'
                                                        }

                                                        response = requests.request("POST", url, headers=headers, data=payload)

                                                        if 'Success' not in response.text:
                                                            data = "Fail Api MA "+ str(response.status_code)
                                                            logger.main_log(data)
                                                except Exception as ex:
                                                    data = "Error Network Monitoring : "+ str(ex)
                                                    logger.main_log(data)
                                                try:
                                                    if minute_diff> datetime.timedelta(minutes=10):
                                                        time_now = datetime.datetime.timestamp(datetime.datetime.now())
                                                        st = int(time_now)
                                                        url = ""

                                                        payload="{\"serial_number\":\""+str(z.DialogSerialNumber)+"\",\"timestamp\":"+str(st)+",\"branch\":\""+branch_name+"\"}"
                                                        headers = {
                                                        'Content-Type': 'application/json'
                                                        }
                                                        response = requests.request("POST", url, headers=headers, data=payload)
                                            
                                                        if 'Success' not in response.text:
                                                            data = "Fail Api HD DATA "+ str(response.status_code)
                                                            logger.main_log(data)
                                                except Exception as ex:
                                                    data = "Error Network Monitoring : "+ str(ex)
                                                    logger.main_log(data)
                     
                                                # ===  Check Sync Data and Connection Between Adapter / machine  =======                    
                                    except Exception as e:
                                        data = "Error Live Data Check: "+ str(e)
                                        logger.main_log(data)
                    else:
                        time_now = datetime.datetime.timestamp(datetime.datetime.now())
                        result_time =time_now - y.DialysisDate
                        days, hours, minutes = result_time.days, result_time.seconds // 3600, result_time.seconds // 60 % 60
                        new_timestamp = int(timestamp)
                        if days == 0:
                            if hours == 0:
                                if minutes >= 10:
                                    try:
                                        url = ""

                                        payload="{\"serial_number\":\""+str(y.SerialNumber)+"\",\"timestamp\":"+str(new_timestamp)+",\"branch\":\""+branch_name+"\"}"
                                        headers = {
                                        'Content-Type': 'application/json'
                                        }
                                        response = requests.request("POST", url, headers=headers, data=payload)
                                        if 'Success' in response.text:
                                            data = "Success to Api "+HD_data+" "+y.SerialNumber+ str(response.status_code)
                                            logger.main_log(data)

                                    except Exception as ex:
                                        data = "Error Network Monitoring : "+ str(ex)
                                        logger.main_log(data)
                                    send.special_gmail(str(y.SerialNumber),branch_name)
    except Exception as ex:
        data = "Error Live Data Monitoring : "+ str(ex)
        logger.main_log(data)

# def Nuc():
#     cpu_usage = psutil.cpu_percent(4)
#     memory_usage = psutil.virtual_memory().percent
#     try:
#         Connect_Monitoring_DB.performance_nuc(cpu_usage,memory_usage)
#     except Exception as ex:
#         data = "Error Nuc Monitoring : "+ str(ex)
#         logger.error(data)
#         print(ex)

                        
if __name__ == "__main__":
    print("Monitoring Version 1.0")
    while True:
        try:
            curr_date = date.today()
            if str(calendar.day_name[curr_date.weekday()]) != "Sunday":
                now= datetime.datetime.now()
                today = datetime.datetime.today()
                jobstart=datetime.datetime(today.year,today.month,today.day,6,today.minute)
                jobstop=datetime.datetime(today.year,today.month, today.day,23,today.minute)
                if((now > jobstart) and (now < jobstop )): 
                    print("start")
                    print("In progress.......")
                    #network()
                    #service_check()
                    main()
                    print("ended at " +str(now))
                    
                else:
                    print("Finish waiting next round .......")
            else:
                print("here")
        except Exception as ex:
            data = "Error Main Monitoring : "+ str(ex)
            logger.main_log(data)
        
        time.sleep(300)
        