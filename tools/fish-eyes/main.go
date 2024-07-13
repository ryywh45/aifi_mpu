package main

import (
	"fmt"
	"fish-eyes/internal/frpc"
)

func main() {
	data, err := frpc.GetFrpcInfo()
	if err != nil {
		fmt.Println("Error: ", err)
	}
	for _, info := range data {
		fmt.Printf("[%v, %v]:", info.Name, info.Status)
		fmt.Printf("%v\n", info.Conf.RemotePort)
	}
}
