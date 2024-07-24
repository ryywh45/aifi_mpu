package frpc

import (
	"io"
	"strconv"
	"net/http"
	"encoding/json"
)

type frpClientConf struct {
	RemotePort uint16 `json:"remote_port"`
	// others are ignored
}

type frpClientInfo struct {
	Name               string        `json:"name"`
	Conf               frpClientConf `json:"conf"`
	// TodayTrafficIn  int64         `json:"today_traffic_in"`
	// TodayTrafficOut int64         `json:"today_traffic_out"`
	// CurConns        int64         `json:"cur_conns"`
	// LastStartTime   string        `json:"last_start_time"`
	// LastCloseTime   string        `json:"last_close_time"`
	Status             string        `json:"status"`
}

type frpClientInfoBody struct {
	Proxies []frpClientInfo `json:"proxies"`
}

func GetFrpcInfo() ([]frpClientInfo, error) {
	resp, err := http.Get("https://frp.aifish.cc/api/proxy/tcp")
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, err
    }

	var data frpClientInfoBody
	err = json.Unmarshal(body, &data)
	if err != nil {
		return nil, err
	}
	return data.Proxies ,nil
}

func GetFrpcInfoSlice() ([][]string, error) {
	var infoMsg [][]string
	infos, err := GetFrpcInfo() 
	if err != nil {
		return nil, err
	}

	for _, info := range infos {
		port := strconv.Itoa(int(info.Conf.RemotePort))
		if port == "0" { port = "" }
		infoMsg = append(infoMsg, []string{info.Name, info.Status, port})
	}
	return infoMsg, nil
}
