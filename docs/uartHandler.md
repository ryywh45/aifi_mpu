## UART通訊對應表
列出了main.py會從mcu接收哪些訊息，以及訊息對應的功能。

訊息內容格式：[( MPU <-> MCU )](./message.md#mpu---mcu)。實做在[這邊](../main/uart/uartHandler.py)。

| 功能 | data1 | data2 | data3 | data4 |
| --- | --- | --- | --- | --- |
| 開始錄影 | 0x01 | 0x00 | X | X |
| 結束錄影 | 0x01 | 0x01 | X | X |
