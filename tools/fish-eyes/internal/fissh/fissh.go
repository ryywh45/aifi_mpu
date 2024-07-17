package fissh

import (
	"fish-eyes/internal/frpc"
	"fmt"
	"log"
	"bytes"
	"strings"
	"strconv"
)

func ListFishMedia(id string, vid bool, pic bool) string {
	port, err := getFishPort(id)
	if err != nil {
		log.Fatal(err)
	}

	client, err := Connect(port)
	if err != nil {
		log.Fatal(err)
	}
	defer client.Close()

	session, err := client.NewSession()
	if err != nil {
		log.Fatal("Failed to create session: ", err)
	}
	defer session.Close()

	var b bytes.Buffer
	session.Stdout = &b

	switch {
	case vid && pic:
		session.Run("ls ~/aifi_mpu/main/service/picam_record/videos ~/aifi_mpu/main/service/picam_record/pictures")
	case vid:
		session.Run("ls ~/aifi_mpu/main/service/picam_record/videos")
	case pic:
		session.Run("ls ~/aifi_mpu/main/service/picam_record/pictures")
	}
	if b.String() == "" {
		return "Empty folder found, nothing inside"
	}
	return b.String()
}

func getFishPort(id string) (string, error) {
	infoList, err := frpc.GetFrpcInfo()
	if err != nil {
		return "", fmt.Errorf("Failed to get frpc info: %v", err)
	}

	for _, info := range infoList {
		if strings.Contains(info.Name, id) && info.Conf.RemotePort != 0 {
			return strconv.Itoa(int(info.Conf.RemotePort)), nil
		}	
	}
	return "", fmt.Errorf("Failed to get fish's port: %v\nTry `fish-eyes status` to check if fish online", err)
}
