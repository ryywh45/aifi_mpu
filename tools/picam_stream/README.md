# 打開rtsp server 串流 pi cam 的影像

使用了[**mediamtx**](https://github.com/bluenviron/mediamtx)這個工具。

因為他直接支援串流pi cam的影像，不用裝其他東西。

## 安裝

### 更新系統
```
sudo apt update
sudo apt full-upgrade
```

### 下載 mediamtx 並解壓縮到`~/mediamtx_v1.8.2`
```
cd ~
curl -L -o https://github.com/bluenviron/mediamtx/releases/download/v1.8.2/mediamtx_v1.8.2_linux_arm64v8.tar.gz
mkdir -p mediamtx_v1.8.2
tar -zxvf mediamtx_v1.8.2_linux_arm64v8.tar.gz -C mediamtx_v1.8.2
```

### Clone這個專案並把設定檔放到`~/mediamtx_v1.8.2`
```
cd ~
git clone https://github.com/ryywh45/aifi_mpu.git
cp aifi_mpu/tools/picam_stream/config.yml ~/mediamtx_v1.8.2
```

## 開始串流
```
cd ~/mediamtx_v1.8.2
./mediamtx
```
現在你可以用 `rtsp://raspi_ip_address:8554/picam` 這個連結來看了。

> 我用 `vlc rtsp://raspi_ip_address:8554/picam` 看不了，
> 
> 但是 `ffplay rtsp://raspi_ip_address:8554/picam` 可以

## 修改pi cam參數

### 設定檔說明
```
  picam:                  // 路徑名稱
    source: rpiCamera     // 影像來源，不能改
    rpiCameraWidth: 320   // 這個不用說明了吧
    rpiCameraHeight: 240
    rpiCameraFPS: 20
```
完整的設定檔在 [config-sample.yml](./config-sample.yml) ，裡面有一些影像處理的東西。

如果有要新增設定，從 [config-sample.yml](./config-sample.yml) 複製該行過來貼上就行。

### Open the config file
```
cd ~/mediamtx_v1.8.2
nano config.yml
```

### Reload config and restart `mediamtx`
要先關掉 `mediamtx`
```
cd ~/mediamtx_v1.8.2
awk '/paths:/{flag=1; print; next} flag{next} 1' mediamtx.yml > temp.yml && mv temp.yml mediamtx.yml
cat config.yml >> mediamtx.yml
./mediamtx
```
