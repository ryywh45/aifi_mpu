# aifi_mpu
## File Structure
```
|--main
|    |--main.py                // serial-websocket bridge
|    |--serial                   
|    |  |--serialHandler.py    // handles imcoming serial data 
|    |  └--
|    |--service                // service is a websocket client on MPU
|    |  |--serviceHandler.py   // handles imcoming service data
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
|    |  |--config.yml
|    |  |--config-sample.yml
|    |  └--README.md
|    |--frpc                   // frp client
|    |  └--
|    └--
└--docs
|    └--
```

## 通訊內容規範
詳細的定義在[message.py](main/communication/message.py)
### Websocket client -> server
- 資料格式：JSON
```
{
    "service": "test.py",      // service名稱，寫檔名
    "data": {
        "key1": "value1",      // 裡面自己定義資料
        "key2": "value2"
    }
}
```

### Websocket server -> client
- 資料格式：JSON
```
{
    "status": 0,               // 0為成功，1為失敗
    "data": {
        "key1": "value1",      // 裡面自己定義資料
        "key2": "value2"
    }
}
```

### MPU <-> MCU
雙向都是這個格式，data的部分日後按照需求定義
範圍在0~255，長度固定為8
- 資料格式：bytes
```
bytes([ord('!'), 8, data1, data2, data3, data4, checksum, checksum])
```
例如data1=1為控制游動，data1=2為控制led等