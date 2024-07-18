## 使用方法
### 0. 先ssh進你的裝置

### 1. clone專案到HOME目錄 

如果clone過就跳過這步
```
cd ~
git clone https://github.com/ryywh45/aifi_mpu.git
```

### 2. 新增資料夾放設定檔

為了避免你之後pull新程式碼的時候衝突
```
mkdir frp-client
rsync -av --exclude='aifi_mpu/tools/frpc/frpc' aifi_mpu/tools/frpc/ "frp-client/"
cd frp-client
```

### 3. 調整設定

打開frpc.ini，修改`[ssh]`的部分(第五行)
```
nano ./frpc.ini
```
如果是魚，修改為`[ssh-fish-3001-pizero]` (3001修改為魚的id)

如果是監控或轉傳器，修改為`[ssh-monitor-003001001-pi3]` (003001001修改為水池編號)

如果是其他的，修改為`[ssh-這邊名字隨便你取]`

接下來你會發現frpc.ini的最上面有:
```
server_addr = x.x.x.x
server_port = 0
```
這兩個參數請找我要，沒有的話不能動

### 4. 給檔案執行權限
```
sudo chmod +x ~/aifi_mpu/tools/frpc/frpc init.sh run.sh
```

### 5. 初始化並啟動  
```
./init.sh
```

### 6. 查看結果

前往以下網址，看看剛剛設定的名稱有沒有出現在上面

(可能要等一下下)

https://frp.aifish.cc/static/#/proxies/tcp
