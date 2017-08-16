from flask import Flask, request
import urllib.request
import json
import requests
import random
import base64
from datetime import datetime 
 
global WEATHER_API_KEY
global LINE_API_KEY
global VISION_API_KEY

LINE_API_KEY = 'secret'
WEATHER_API_KEY  = 'secret'
VISION_API_KEY = 'secret'

app = Flask(__name__)
 
@app.route('/')
def index():
    return 'Hi!'

@app.route('/callback', methods=['POST'])
def callback():
    replyStack = []
    json_line = request.get_json()
    json_line = json.dumps(json_line)
    decoded = json.loads(json_line)
    replyToken = decoded["events"][0]['replyToken']
    timestamp = decoded["events"][0]['timestamp']
    
    if decoded["events"][0]['message']['type'] == 'location':
        # Location weather forecast
        latitude = decoded["events"][0]['message']['latitude']
        longitude = decoded["events"][0]['message']['longitude']
        replyStack.extend(forecast(latitude,longitude))

    elif decoded["events"][0]['message']['type'] == 'text':
        text = decoded["events"][0]['message']['text'].lower().strip()
        if text in ['help','h','?','ใช้ยังไง','เล่นยังไง','ทำไรได้','ทำอะไรได้บ้าง','ทำไรได้บ้าง']:
            replyStack.append('List คำสั่ง..\n'+'- !bus xx ข้อมูลรถเมล์\n'+'- !manga xxx อัพเดตการ์ตูนล่าสุด\n'+'- !dota xx อัพเดตออนไลน์ล่าสุด\n'+'- !กินไรดี random ที่กิน\n'+'*ใส่ ! หน้าคำสั่งทุกครั้งน้า ^^')
            sendText(replyToken,replyStack)
            return '',200
        cmd = (text[0] == '!')
        if cmd:
            argv = text.split()
            op = argv[0][1:].strip()
            if op in ['mg','อ่าน','manga','การ์ตูน']:
                # Update manga
                parm = ('').join(argv[1:]).strip()
                if parm in ['onepunchman','opm','ไซตามะ']:
                    # One punch man update
                    name,link = updateOne_punch_man()
                    replyStack.append(name)
                    replyStack.append(link)
                elif parm in ['onepiece','op']:
                    # One piece update
                    name,link = updateOne_piece()
                    replyStack.append(name)
                    replyStack.append(link)
                elif parm in ['titan','attackontitan','aot']:
                    # Titan update
                    name,link = updateTitan()
                    replyStack.append(name)
                    replyStack.append(link)
            elif op in ['กินไรดี','กินอะไรดี']:
                foodlist_file = open('foodlist.txt','r')
                food_list = foodlist_file.read().split(',')
                replyStack.append(food_list[random.randrange(len(food_list))])
                foodlist_file.close()
            elif op in ['รถเมล์','รถ','bus','เมล์']:
                parm = ('').join(argv[1:]).strip()
                num = ''
                for p in parm:
                    if p in '0123456789๑๒๓๔๕๖๗๘๙๐':
                        num+=p
                name,line = busLine(num)
                #,name2,line2
                if name == 'error':
                    replyStack.append('ไม่พบข้อมูลสายนี้')
                else:
                    replyStack.append(name)
                    replyStack.append(line)
                    #replyStack.append(name2)
                    #replyStack.append(line2)
            elif op in ['dota','dot']:
                #dota update
                parm = ('').join(argv[1:]).strip()
                if parm in ['runrun','run','รัน','รันรัน','รันๆ','คุณย่า','gmdelivery','คุณย่าดิลิเวอรี่','ป้าแมรี่']:
                    last_matches = dota2API('325282180')
                    replyStack.extend(last_matches)
                elif parm in ['ตั๊ก','takk','tak','ตัก','wolf','hero']:
                    last_matches = dota2API('372480482')
                    replyStack.extend(last_matches)
                elif parm in ['tum','ตั้ม','tummy','ตัม']:
                    last_matches = dota2API('197042775')
                    replyStack.extend(last_matches)
                elif parm in ['park','ปาร์ค','ปาค']:
                    last_matches = dota2API('338501985')
                    replyStack.extend(last_matches)
                elif parm in ['max','แม๊ค','แม๊ก','แมค','แมก']:
                    last_matches = dota2API('397465594')
                    replyStack.extend(last_matches)
        elif text in ['สยามรถติดไหม','สยามรถติดมั๊ย','สยามรถติดมัย']:
            replyStack.append('ไม่รู้ค้าบ 555555555')
        elif text in ['ญ่วน','ย่วน']:
            replyStack.append('ชื่อกอล์ฟไม่ใช่เหรอจ้ะ 555555')
        else:
            replyStack.append('ไม่รู้จักคำสั่ง TT')

    elif decoded["events"][0]['message']['type'] == 'image':
        id = decoded["events"][0]['message']['id']
        img = getContent(id)
        img64 = str(base64.b64encode(img))[2:-1]
        labeled = cloudVision(img64)
        for i in range(5):
            name = labeled["responses"][0]["labelAnnotations"][i]["description"]
            score = labeled["responses"][0]["labelAnnotations"][i]["score"]
            score = str(score)
            score = score if len(score) <= 6 else score[:6]
            replyStack.append(name.upper() + ": " + score)
    else:
        replyStack.append(json_line)
        
    replyStack = replyStack if len(replyStack) <= 5 else replyStack[:5]
    sendText(replyToken,replyStack)
    return '',200

def updateOne_punch_man():
    site = urllib.request.urlopen('http://www.oremanga.com/78-1-One+Punch+Man.html')
    site = site.read()
    site = site.decode('utf8')
    pos = site.find('One Punch Man ตอนที่')
    cut = site[pos:pos+150]
    name = cut[:cut.find('<')]
    cutlink = site[pos-150:pos]
    link = cutlink[cutlink.find('<a href=')+9:cutlink.find('style=')]
    link = "http://www.oremanga.com/"+link.strip()[:-1]
    return name,link

def updateTitan():
    site = urllib.request.urlopen('http://www.oremanga.com/11-1-Attack+on+Titan.html')
    site = site.read()
    site = site.decode('utf8')
    pos = site.find('Attack on Titan - ตอนที่')
    cut = site[pos:pos+150]
    name = cut[:cut.find('<')]
    cutlink = site[pos-150:pos]
    link = cutlink[cutlink.find('<a href=')+9:cutlink.find('style=')]
    link = "http://www.oremanga.com/"+link.strip()[:-1]
    return name,link

def updateOne_piece():
    site = urllib.request.urlopen('http://go-chan.blogspot.com/p/manga.html#onepiece')
    site = site.read()
    site = site.decode('utf8')
    pos = site.find('<b>One Piece')
    cut = site[pos:pos+150]
    cutlink = cut[cut.find('<a href='):]
    link = cutlink[9:cutlink.find('>')-1]
    name = cut[3:cut.find('</b>')]
    return name,link

def forecast(latitude,longitude):
    replyStackmini = []
    html = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?lat='+str(latitude)+'&lon='+str(longitude)+'&appid='+WEATHER_API_KEY)
    html = html.read()
    json_fc = json.loads(html)
    main_status = json_fc['weather'][0]['main']
    status = json_fc['weather'][0]['description']
    clouds_percent = json_fc['clouds']['all']
    place_a = json_fc['name']
    place_b = json_fc['sys']['country']
    if main_status.lower() == 'clouds':
        if clouds_percent < 50:
            replyStackmini.append('มีเมฆเฉยๆชิวๆ')
        else:
            replyStackmini.append('มีเมฆมากนะ!')
    elif main_status.lower() == 'rain':
        replyStackmini.append('ฝนตกจ้า เอาร่มมาไหมเนี่ย?')
    summary = "info: " + status + "\nclouds: " + str(clouds_percent) + "%\n" + "@" + place_a +", "+ place_b 
    replyStackmini.append(summary)
    return replyStackmini
 
def sendText(replyToken, textList):
    LINE_API = 'https://api.line.me/v2/bot/message/reply'
    Authorization = LINE_API_KEY
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization':Authorization
    }
    msgs = []
    for text in textList:
        msgs.append({
            "type":"text",
            "text":text
        })
    data = json.dumps({
        "replyToken":replyToken,
        "messages":msgs
    })
 
    r = requests.post(LINE_API, headers=headers, data=data)

def getContent(id):
    LINE_API = 'https://api.line.me/v2/bot/message/'+str(id)+'/content'
    Authorization = LINE_API_KEY
    r = requests.get(LINE_API, headers={'Authorization': Authorization})
    r = r.content
    return r

def cloudVision(img):
    VISION_API = 'https://vision.googleapis.com/v1/images:annotate?key=' + VISION_API_KEY
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({
        "requests":[
        {
            "image":{
                "content":img
            },
            "features":[
                {
                    "type":"LABEL_DETECTION",
                    "maxResults":5
                }
            ]
        }
        ]
    })
    r = requests.post(VISION_API, headers=headers, data=data)
    r = r.json()
    return r

def busLine(n):
    site = urllib.request.urlopen('http://bmta.doodroid.com/bus/'+str(n))
    site = site.read()
    site = site.decode('utf8')
    word = 'ต้นทาง-ปลายทาง</td><td>'
    pos = site.find(word)
    cut_large = site[pos+len(word):]
    cut = site[pos+len(word):pos+5000]
    name = cut[:cut.find('<')]
    if name[:6] == ' Error':
        return 'error',''
    pos = 0
    stop_list = []
    while pos != -1:
        pos = cut.find('title=\"')
        line = cut[pos:]
        cut1 = line[line.find('\">'):]
        busStop = cut1[2:cut1.find('</a>')]
        if len(busStop) > 0:
            stop_list.append(busStop)
        cut = cut1[cut1.find('</a>'):]
    str_stop = (', ').join(stop_list)
    '''word2 = 'ต้นทาง-ปลายทาง</td><td>'
    pos2 = cut_large.find(word2)
    cut_large = cut_large[pos2+len(word2):]
    cut2 = cut_large[:pos2+5000]
    name2 = cut2[:cut2.find('<')]
    pos = 0
    stop_list = []
    while pos != -1:
        pos = cut2.find('title=\"')
        line = cut2[pos:]
        cut3 = line[line.find('\">'):]
        busStop = cut3[2:cut3.find('</a>')]
        if len(busStop) > 0:
            stop_list.append(busStop)
        cut2 = cut3[cut3.find('</a>'):]
    str_stop2 = (', ').join(stop_list)
    print(name)
    print(str_stop)
    print(name2)
    print(str_stop2)'''
    return name, str_stop#, name2, str_stop2

def dota2API(id):
    # run run = 325282180
    DOTA2_API = 'https://api.opendota.com/api/players/'+str(id)+'/recentMatches'
    DOTA2_HERO = 'https://api.opendota.com/api/heroes'
    headers = {'Content-Type': 'application/json'}
    hero = requests.get(DOTA2_HERO, headers=headers).json()
    r = requests.get(DOTA2_API, headers=headers)#, data=data)
    r = r.json()
    printed = ['','','','','']
    for i in range(5):
        printed[i] += hero[r[i]['hero_id']-1]['localized_name'] + '\n'
        printed[i] += 'K/D/A: '+ str(r[i]['kills']) + '/' + str(r[i]['deaths']) + '/' + str(r[i]['assists']) +'\n'
        current_time = datetime.utcnow()
        time_val = r[i]['start_time']
        diff = (current_time - datetime.utcfromtimestamp(int(time_val))).total_seconds()
        printed[i] += str(diff//3600)+' hour(s) ago'
    return printed

if __name__ == '__main__':
    app.run(debug=True)  