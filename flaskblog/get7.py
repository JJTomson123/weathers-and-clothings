# import packages
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import datetime
import os


import urllib.request
import zipfile 
import lxml

def get7():
    # set dir 
    today = str(datetime.date.today())
    cwb_data = os.path.join(os.path.dirname(__file__),'cwb_weather_data')
    if not os.path.exists(cwb_data):
        os.mkdir(cwb_data)
    # connect api
    #res ="http://opendata.cwb.gov.tw/opendataapi?dataid=F-D0047-093&authorizationkey=CWB-3FB0188A-5506-41BE-B42A-3785B42C3823"
    #urllib.request.urlretrieve(res,"F-D0047-093.zip")
    f=zipfile.ZipFile('F-D0047-093.zip')
    file = ['63_Week24_CH.xml']
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
                district = location.find_all("locationName")#[i].text
                weather = location.find_all("weatherElement")
                time = weather[1].find_all("startTime")
                for j in range(0,len(time)):
                    x = time[j].text.split("T")
                    DAY.append(x[0])
                    time_1 = x[1].split("+")
                    DISTRICT.append(district)
                for t  in weather[0].find_all("value"):
                    T.append(t.text)
                for td  in weather[1].find_all("value"):
                    TD.append(td.text)
                for rh  in weather[2].find_all("value"):
                    RH.append(rh.text)
                for wd  in weather[5].find_all("value"):
                    WD.append(wd.text)  
                for at  in weather[8].find_all("value"):
                    AT.append(at.text)
                wx = weather[12].find_all("value")
                for w in range(0,len(wx),2):
                    Wx.append(wx[w].text)
        except:
            break

    f.close()
    data = {"DISTRICT":DISTRICT,"DAY" : DAY,"T":T,"TD" : TD,"RH":RH,"WD" : WD,"AT" : AT,"Wx": Wx}
    df = pd.DataFrame(data,columns=["DISTRICT","DAY","T","TD","RH","WD","AT","Wx"])

    file_path = os.getcwd()
    save_name = "taiwan_cwb_7_day.csv"
    save_name = os.path.join(file_path,cwb_data,save_name)
    df.to_csv(save_name,index=False,encoding="utf_8_sig")

