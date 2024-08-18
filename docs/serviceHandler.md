## Websocket通訊對應表
列出了main.py會從各個Service接收哪些Websocket訊息，以及訊息對應的功能。

訊息內容格式：[( client -> server )](./message.md#websocket-client---server)。實做在[這邊](../main/service/serviceHandler.py)。

如果要查看各個Service的Websocket通訊對應表，請參考該Service的Readme文件。


| Service name | 功能 | data欄位內容 |
| --- | --- | --- |
| [ test.py ] | 傳資料到Serial | 含有"to_serial"欄位 |
| [ test.py ] | 開啟錄影 | "startRecording" |
| [ test.py ] | 關閉錄影 | "stopRecording" |
| [ test.py ] | 拍一張照片 | "take-a-pic" |