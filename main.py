#!/Users/yinpsong/anaconda/envs/python27/bin
#-*-coding:utf-8-*-
import time
import logging
import requests

from basiclogger import LOGGING
from holiday import holidays
import mailutil


def get_car_list(wx):
    currentTime = time.localtime()
    currentStr = time.strftime("%Y-%m-%d %H:%M:%S", currentTime)
    url = "http://free_bus_ticket.fyxmt.com/interface/ticketList?queryDate=%s" % currentStr
    headers = dict()
    headers[
        "User-Agent"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 11_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15F79 MicroMessenger/6.7.0 NetType/WIFI Language/zh_CN"
    headers["Referer"] = "http://free_bus_ticket.fyxmt.com/front-end/jianwuqiangpiao/buy-tickets.html?wechatNo=%s" % wx
    headers["X-Requested-With"] = "XMLHttpRequest"
    
    req = requests.get(url, headers=headers)
    bus_list = req.json().get("obj", {}).get("busTrips", [])
    currentHour = currentTime.tm_hour
    if 12<=currentHour<=17:
        return order_gohome_ticket(bus_list)
    else:
        return order_gowork_ticket(bus_list)
    return None

def order_gohome_ticket(bus_list):
    currentTime = time.localtime()
    today = time.strftime("%Y-%m-%d", currentTime)
    for bus in bus_list:
        for trip in bus.get("trips", []):
            if trip["fromPlace"] == "产业园停车场".decode("utf-8") and trip["toPlace"] == "金尚路地铁站".decode("utf-8") and trip["orderTimeEnd"] == today + " 18:10:00":
                logging.info("%s %s %s " % (trip["fromPlace"], trip["toPlace"], trip["orderTimeEnd"]))
                return trip["id"]

def order_gowork_ticket(bus_list):
    current = time.localtime()
    orderDate = time.strftime("%Y-%m-%d",current)
    orderTime = None
    if 0<=current.tm_hour<=8:
        orderTime = orderDate + " 08:10:00"
    else:
        tomorrow = time.time()+24*3600
        tomorrow = time.localtime(tomorrow)
        orderDate = time.strftime("%Y-%m-%d",tomorrow)
        orderTime = orderDate + " 08:10:00"
    
    for bus in bus_list:
        for trip in bus.get("trips", []):
            if trip["fromPlace"] == "金尚路地铁站".decode("utf-8") and trip["toPlace"] == "产业园停车场".decode("utf-8") and trip["orderTimeEnd"] == orderTime:
                logging.info("%s %s %s " % (trip["fromPlace"], trip["toPlace"], trip["orderTimeEnd"]))
                return trip["id"]


def order_ticket(wx, bus_id):
    url = "http://free_bus_ticket.fyxmt.com/interface/grabTicket"
    headers = dict()
    headers[
        "User-Agent"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 11_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15F79 MicroMessenger/6.7.0 NetType/WIFI Language/zh_CN"
    headers["Referer"] = "http://free_bus_ticket.fyxmt.com/front-end/jianwuqiangpiao/buy-tickets.html?wechatNo=%s" % wx
    headers["X-Requested-With"] = "XMLHttpRequest"

    data = dict()
    data["wechatNo"] = wx
    data["id"] = bus_id

    req = requests.post(url, json=data)
    logging.info(req.json().get("msg"))
    return req.json().get("msg")

def check_my_ticket(wx):
    currentTime = time.localtime()
    currentHour = currentTime.tm_hour

    headers = dict()
    headers[
        "User-Agent"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 11_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15F79 MicroMessenger/6.7.0 NetType/WIFI Language/zh_CN"
    headers["Referer"] = "http://free_bus_ticket.fyxmt.com/front-end/jianwuqiangpiao/my-ticket.html?wechatNo=%s" % wx
    headers["X-Requested-With"] = "XMLHttpRequest"
    headers["Host"] = "free_bus_ticket.fyxmt.com"
    headers["Origin"] = "http://free_bus_ticket.fyxmt.com"
    my_ticket_url = "http://free_bus_ticket.fyxmt.com/interface/myTicketList"

    data = dict()
    data["wechatNo"] = wx

    req = requests.post(my_ticket_url, json=data)
    ticketList = req.json().get("obj",{}).get("MyTicketList",[])


    def check_go_home_ticket(ticketList,dateStr):
        for ticket in ticketList:
            schedule = ticket.get("schedule", {})
            if schedule["fromPlace"] == "产业园停车场".decode("utf-8") and schedule["toPlace"] == "金尚路地铁站".decode("utf-8") and schedule["orderTimeEnd"] == dateStr + " 18:10":
                message = u"已预定回家的票 %s 从 %s 到 %s" % (schedule["orderTimeEnd"],schedule["fromPlace"], schedule["toPlace"])
                logging.info(message)
                return (True,message)
        return (False,None)

    def check_go_work_ticket(ticketList,dateStr):
        for ticket in ticketList:
            schedule = ticket.get("schedule", {})
            if schedule["fromPlace"] == "金尚路地铁站".decode("utf-8") and schedule["toPlace"] == "产业园停车场".decode("utf-8") and schedule["orderTimeEnd"] == dateStr + " 08:10":
                message = u"已预定上班的票 %s 从 %s 到 %s" % (schedule["orderTimeEnd"], schedule["fromPlace"], schedule["toPlace"])
                logging.info(message)
                return (True,message)
        return (False,None)

    if 12<=currentHour<=18:
        dateStr = time.strftime("%Y-%m-%d",currentTime)
        return check_go_home_ticket(ticketList,dateStr)
    elif 19<=currentHour<=23:
        tomorrow = time.localtime(time.time()+24*3600)
        dateStr = time.strftime("%Y-%m-%d", tomorrow)
        return check_go_work_ticket(ticketList,dateStr)
    elif 0<=currentHour<=8:
        dateStr = time.strftime("%Y-%m-%d", currentTime)
        return check_go_work_ticket(ticketList, dateStr)
    else:
        return (False,None)

if __name__ == '__main__':
    LOGGING("banche")
    today = time.localtime()
    today_str = time.strftime("%Y%m%d",today)
    if (today_str in holidays) or (today.tm_wday>=5):
        logging.info(u"今天是节假日，不用抢票")
        exit(0)
    if 8<=today.tm_hour<=11:
        logging.info(u"8点至12点之间不必执行抢票")
        exit(0)
    wx_id = "ofqo-uE7MMra_9NrQDDv_LHH91mY"
    success,message = check_my_ticket(wx_id)
    if success == True:
        mailutil.send_mail("your_qq@qq.com",message)
        exit(0)
    while True:
        try:
            bus_id = get_car_list(wx_id)
            break
        except:
            time.sleep(3)
            continue
    if bus_id is None:
        logging.info(u"没有你想要的班次")
    else:
        while True:
            try:
                text = order_ticket(wx_id, bus_id)
            except Exception as e:
                continue
            if text.find("成功".decode("utf-8")) >= 0:
                success, message = check_my_ticket(wx_id)
                if success == True:
                    logging.info(u"抢票结束")
                    mailutil.send_mail("your_qq@qq.com", message)
                    break
            elif text.find("抢完了".decode("utf-8")) >= 0:
                if 12<=today.tm_hour<=18:
                    message = u"没抢到回家的票"
                else:
                    message = u"没抢到上班的票"
                logging.info(message)
                mailutil.send_mail("your_qq@qq.com", message)
                break

