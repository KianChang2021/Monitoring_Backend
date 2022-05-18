import socket,datetime,logging
import logger

def restart_Ma(ip):
    try:
        mss = "Restarted" + str(datetime.now)
        logger.ma_log(mss)
        TCP_IP = str(ip)
        TCP_PORT = 5003
        BUFFER_SIZE = 1024
        MESSAGE = "1"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        s.send(MESSAGE.encode())
        s.close()
    except Exception as ex:
        data = "Error in restart MA: " +str(ex)
        logger.error(data)

if __name__ == "__main__":
    restart_Ma('192.168.1.1')