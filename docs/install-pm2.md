## Install PM2
pm2官網的教學在[這邊](https://pm2.io/docs/runtime/guide/installation/)
，但官網給的debian install script沒用，以下提供用npm安裝的方法：
### 1. Install nvm
以下是目前nvm最新版(v0.40.0)的安裝指令，可以到[nvm github](https://github.com/nvm-sh/nvm?tab=readme-ov-file#installing-and-updating)
查看最新版本的指令。
```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
```
### 2. Logout and login
要登出再登入，讓nvm生效。
```
logout
```
### 3. Install pm2
```
nvm install --lts node
npm install pm2 -g
```