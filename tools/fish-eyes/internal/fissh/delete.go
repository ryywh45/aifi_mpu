package fissh

import (
	"log"
	"strings"
	"github.com/pkg/sftp"
)

func DelFishMedia(id string, option Option){
	var srcPath string
	var filenames []string

	switch option.Type {
	case OptionDelTagged:
		filenames = filtByTagged(id)
	case OptionDelUnTagged:
		filenames = filtByUnTagged(id)
	case OptionDelAll:
		filenames = ListFishMediaSlice(id, true, true)
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
		if err := sftpClient.Remove(srcPath + "/" + filename); err != nil {
			log.Fatal("Failed to remove file: ", err)
		}
	}
}
