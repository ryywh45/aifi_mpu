package fissh

import (
	"bytes"
	"fish-eyes/internal/frpc"
	"fmt"
	"log"
	"strconv"
	"strings"

	"golang.org/x/crypto/ssh"
)

var vidPath string = "/home/" + username + "/aifi_mpu/main/service/picam_record/videos"
var picPath string = "/home/" + username + "/aifi_mpu/main/service/picam_record/pictures"

type optionType int

type Option struct {
	Type       optionType
	Value      string
	BoolValue  bool
}

const (
	OptionFilename optionType = iota
	OptionDate
	OptionLatestVid
	OptionLatestPic
	OptionTagged
	OptionUnTagged
	OptionAll
	OptionDelTagged
	OptionDelUnTagged
	OptionDelAll
)

func ListFishMedia(id string, vid bool, pic bool) string {
	client := connectById(id)
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
		session.Run(fmt.Sprintf("ls %v %v", vidPath, picPath))
	case vid:
		session.Run(fmt.Sprintf("ls %v", vidPath))
	case pic:
		session.Run(fmt.Sprintf("ls %v", picPath))
	}
	if b.String() == "" {
		return "Empty folder found, nothing inside"
	}
	return b.String()
}

func ListFishMediaSlice(id string, vid, pic bool) []string {
	rawStr := ListFishMedia(id, vid, pic)
	slice := []string{}
	for _, str := range strings.Split(rawStr, "\n") {
		if strings.HasPrefix(str, "202") {
			slice = append(slice, str)
		}
	}
	return slice
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

func connectById(id string) *ssh.Client {
	port, err := getFishPort(id)
	if err != nil {
		log.Fatal(err)
	}

	client, err := connect(port)
	if err != nil {
		log.Fatal(err)
	}

	return client
}
