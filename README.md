# aifi_mpu

```
|--main
|    |--frpc                   // frp client
|    |  └--
|    |--uart                   // communication with MCU
|    |  |--uartHandler.py      // serial-websocket bridge
|    |  └--
|    |--service                // services on MPU
|    |  |--template.py         // template for new service
|    |  |--picam_record        
|    |  |  |--picam_record.py  // picam recording service
|    |  |  └--videos           // saved videos
|    |  └--
|--tools
|    |--picam_stream           // push stream to rtsp server
|    |  |--config.yml
|    |  |--config-sample.yml
|    |  └--README.md
└--docs
|    └--
```

### todo
- 測試後上傳frpc部分
- uartHandler加上log
- 與mcu通訊方式待定
- 以上完成後為v1.0，後續建新branch開發
