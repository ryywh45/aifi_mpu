## File Structure
```
|--main
|    |--main.py                // serial-websocket bridge
|    |--uart                   
|    |  |--uartHandler.py      // handles incoming serial data 
|    |  └--
|    |--service                // service is a websocket client on MPU
|    |  |--serviceHandler.py   // handles incoming service data
|    |  |--template.py         // template for new service
|    |  |--picam_record        
|    |  |  |--picam_record.py  // picam recording service
|    |  |  └--videos           // saved videos
|    |  └--
|    |--communicaton
|    |  |--message.py          // message format of websocket
|    |  └--
|    └--
|--tools
|    |--picam_stream           // push stream to rtsp server
|    |  └-- ...
|    |--frpc                   // frp client setup guide
|    |  └-- ...
|    └--fish-eyes              // get video/picture that inside fish
|    |  └-- ...
└--docs
|    └--
```

## 佈署專案
### 0. Requirements
- Python 3.6+
- pip
- `sudo apt install python3-venv`
- pm2 [(安裝教學)](./install-pm2.md)

### 1. Clone專案
```
git clone https://github.com/ryywh45/aifi_mpu.git
```
### 2. 建立虛擬環境並安裝相依套件
```
cd aifi_mpu/main
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt
```
### 3. 啟動main.py
```
pm2 start main.py --interpreter venv/bin/python3
```
### 4. 設定pm2開機自動啟動
pm2會提示你複製並執行一個指令，照做就行。
```
pm2 startup
```
