# import packages
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import datetime
import os
import pyodbc

import urllib.request
import zipfile 
import lxml

def getw():
    # set dir 
    today = str(datetime.date.today())
    cwb_data = os.path.join(os.path.dirname(__file__),'cwb_weather_data')
    if not os.path.exists(cwb_data):
        os.mkdir(cwb_data)
    # connect api
    res ="http://opendata.cwb.gov.tw/opendataapi?dataid=F-D0047-093&authorizationkey=CWB-3FB0188A-5506-41BE-B42A-3785B42C3823"
    urllib.request.urlretrieve(res,"F-D0047-093.zip")
    f=zipfile.ZipFile('F-D0047-093.zip')
    file = ['63_72hr_CH.xml']
    CITY = []
    DISTRICT = []
    GEOCODE = []
    DAY = []
    TIME = []
    T = []
    TD = []
    WD = []
    WS = []
    BF = []
    AT = []
    Wx = []
    Wx_n = []
    get_day = []
    RH = []
    for filename in file:
        try:
            data = f.read(filename).decode('utf8')
            soup = BeautifulSoup(data,"xml")
            city = soup.locationsName.text
            a = soup.find_all("location")
            for i in range(0,len(a)):
                location = a[i]
                district = location.find_all("locationName")[0].text
                geocode = location.geocode.text
                weather = location.find_all("weatherElement")
                time = weather[1].find_all("dataTime")
                for j in range(0,len(time)):
                    x = time[j].text.split("T")
                    DAY.append(x[0])
                    time_1 = x[1].split("+")
                    TIME.append(time_1[0])
                    CITY.append(city)
                    DISTRICT.append(district)
                    GEOCODE.append(geocode)
                    get_day.append(today)
                for t  in weather[0].find_all("value"):
                    T.append(t.text)
                for td  in weather[1].find_all("value"):
                    TD.append(td.text)
                for rh  in weather[2].find_all("value"):
                    RH.append(rh.text)
                for wd  in weather[5].find_all("value"):
                    WD.append(wd.text)  
                ws = weather[6].find_all("value")
                for k  in range(0,len(ws),2):
                    WS.append(ws[k].text)
                    BF.append(ws[k+1].text)
                for at  in weather[8].find_all("value"):
                    AT.append(at.text)
                wx = weather[9].find_all("value")
                for w in range(0,len(wx),2):
                    Wx.append(wx[w].text)
                    Wx_n.append(wx[w+1].text)
                rain1 = weather[3].find_all("value")

        except:
            break
    f.close()

    data = {"CITY":CITY,"DISTRICT":DISTRICT,"GEOCODE":GEOCODE,"DAY" : DAY,"TIME" : TIME,"T":T,"TD" : TD,"RH":RH,
            "WD" : WD,"WS" : WS,"BF":BF,"AT" : AT,"Wx": Wx,"Wx_n":Wx_n,"get_day":get_day}
    df = pd.DataFrame(data,columns=["CITY","DISTRICT","GEOCODE","DAY","TIME","T","TD","RH","WD","WS","BF","AT","Wx","Wx_n","get_day"])
    file_path = os.getcwd()
    save_name = "taiwan_cwb.csv"
    save_name = os.path.join(file_path,cwb_data,save_name)
    df.to_csv(save_name,index=False,encoding="utf_8_sig")

getw()