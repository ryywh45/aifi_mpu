package frpc

import (
	"io"
	"net/http"
	"encoding/json"
)

type FrpClientConf struct {
	RemotePort uint16 `json:"remote_port"`
	// others are ignored
}

type FrpClientInfo struct {
	Name               string        `json:"name"`
	Conf               FrpClientConf `json:"conf"`
	// TodayTrafficIn  int64         `json:"today_traffic_in"`
	// TodayTrafficOut int64         `json:"today_traffic_out"`
	// CurConns        int64         `json:"cur_conns"`
	// LastStartTime   string        `json:"last_start_time"`
	// LastCloseTime   string        `json:"last_close_time"`
	Status             string        `json:"status"`
}

type FrpClientInfoBody struct {
	Proxies []FrpClientInfo `json:"proxies"`
}

func GetFrpcInfo() ([]FrpClientInfo, error) {
	resp, err := http.Get("https://frp.aifish.cc/api/proxy/tcp")
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, err
    }

	var data FrpClientInfoBody
	err = json.Unmarshal(body, &data)
	if err != nil {
		return nil, err
	}
	return data.Proxies ,nil
}
