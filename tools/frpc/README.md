## 使用方法
0. 先ssh進你的裝置
1. clone專案到HOME目錄然後cd進去 
如果clone過就cd進去就好
```
cd ~
git clone https://github.com/ryywh45/aifi_mpu.git
cd aifi_mpu/tools/frpc
```
2. 設定名稱 
打開frpc.ini，修改`[ssh]`的部分(第四行)
```
nano ./frpc.ini
```
如果是魚，修改為`[ssh-fish-3001-pizero]` (3001修改為魚的id)
如果是監控或轉傳器，修改為`[ssh-monitor-003001001-pi3]` (003001001修改為水池編號)
如果是其他的，修改為`[ssh-這邊名字隨便你取]`
3. 給檔案執行權限
```
sudo chmod +x frpc init.sh run.sh
```
4. 初始化並啟動  
```
./init.sh
```
5. 查看結果
前往以下網址，看看剛剛設定的名稱有沒有出現在上面
(可能要等一下下)
https://frp.aifish.cc/static/#/proxies/tcp
