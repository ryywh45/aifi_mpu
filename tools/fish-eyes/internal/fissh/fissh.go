package fissh

import (
	"bytes"
	"fish-eyes/internal/frpc"
	"fmt"
	"log"
	"strconv"
	"strings"

	"github.com/pkg/sftp"
	"golang.org/x/crypto/ssh"
)

var vidPath string = "/home/" + username + "/aifi_mpu/main/service/picam_record/videos"
var picPath string = "/home/" + username + "/aifi_mpu/main/service/picam_record/pictures"

type optionName int

const (
	OptionFilename optionName = iota
	OptionDate
	OptionLatestVid
	OptionLatestPic
)

type Option struct {
	Name optionName
	Value string
}

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

func GetFishMedia(id string, option Option, dstPath string) {
	var srcPath string
	var filenames []string

	switch option.Name {
	case OptionFilename:
		filenames = []string{option.Value}
	case OptionDate:
		filenames = getByDate(id, option.Value)
	case OptionLatestVid:
		filenames = getByLatestVid(id, option.Value)
	case OptionLatestPic:
		filenames = getByLatestPic(id, option.Value)
	default:
		log.Fatal("Invaild option")
	}

	if len(filenames) == 0 {
		log.Fatal("No maching files found.")
	}

	client := connectById(id)
	defer client.Close()

	sftpClient, err := sftp.NewClient(client)
	if err != nil {
		log.Fatal(err)
	}
	defer sftpClient.Close()

	for _, filename := range filenames {
		switch {
		case strings.Contains(filename, ".mp4"):
			srcPath = vidPath
		case strings.Contains(filename, ".png"):
			srcPath = picPath
		default:
			continue
		}
		copySingleFile(sftpClient, filename, srcPath, dstPath)
	}
}

func getByDate(id, date string) []string {
	var filenames []string
	for _, filename := range ListFishMediaSlice(id, true, true) {
		if strings.HasPrefix(filename, date) {
			filenames = append(filenames, filename)
		}
	}
	return filenames
}

func getByLatestVid(id, count string) []string {
	var filenames []string = ListFishMediaSlice(id, true, false)
	c, err := strconv.Atoi(count)
	if err != nil {
		log.Fatal(err)
	}
	return filenames[len(filenames) - c:] 
}

func getByLatestPic(id, count string) []string {
	var filenames []string = ListFishMediaSlice(id, false, true)
	c, err := strconv.Atoi(count)
	if err != nil {
		log.Fatal(err)
	}
	return filenames[len(filenames) - c:] 
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
