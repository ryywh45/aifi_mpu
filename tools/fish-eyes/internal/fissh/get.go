package fissh

import(
	"log"
	"strings"
	"github.com/pkg/sftp"
)

func GetFishMedia(id string, option Option, dstPath string) {
	var srcPath string
	var filenames []string

	switch option.Type {
	case OptionFilename:
		filenames = []string{option.Value}
	case OptionDate:
		filenames = filtByDate(id, option.Value)
	case OptionLatestVid:
		filenames = filtByLatestVid(id, option.Value)
	case OptionLatestPic:
		filenames = filtByLatestPic(id, option.Value)
	case OptionTagged:
		filenames = filtByTagged(id)
	case OptionUnTagged:
		filenames = filtByUnTagged(id)
	case OptionAll:
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
		copySingleFile(sftpClient, filename, srcPath, dstPath)
	}
}

