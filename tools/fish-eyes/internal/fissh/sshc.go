package fissh

import (
	"fmt"
	"io"
	"log"
	"net"
	"os"
	"path/filepath"
	"runtime"
	"strings"

	"github.com/pkg/sftp"
	"golang.org/x/crypto/ssh"
	"golang.org/x/crypto/ssh/agent"
)

var hostname string
var username string = "aifi-fish"

func connect(port string) (*ssh.Client, error) {
	askHostname()
	var client *ssh.Client
	var err error
	config := &ssh.ClientConfig{
		User:            username,
		HostKeyCallback: ssh.InsecureIgnoreHostKey(),
	}
	addr := hostname + ":" + port

	if runtime.GOOS != "windows" {
		conn, err := net.Dial("unix", os.Getenv("SSH_AUTH_SOCK"))
		if err == nil {
			agentClient := agent.NewClient(conn)
			config.Auth = []ssh.AuthMethod{ssh.PublicKeysCallback(agentClient.Signers)}
			client, err = ssh.Dial("tcp", addr, config)
			if err == nil {
				// connected
				return client, nil
			}
		}
	}

	config.Auth = []ssh.AuthMethod{ssh.Password(askPassword())}
	client, err = ssh.Dial("tcp", addr, config)
	if err != nil {
		return nil, fmt.Errorf("unable to connect to fish: %v", err)
	}

	return client, nil
}

func ChangeUsername(name string) {
	username = name
	vidPath = "/home/" + username + "/aifi_mpu/main/service/picam_record/videos"
	picPath = "/home/" + username + "/aifi_mpu/main/service/picam_record/pictures"
}

func askHostname() {
	content, err := os.ReadFile(filepath.Join(".", "host"))
	if err != nil {
		fmt.Print("Fish's ip address: ")
		fmt.Scan(&hostname)
		os.WriteFile("./host", []byte(hostname), 0644)
		return
	}
	hostname = string(content)
}

func askPassword() string {
	var password string
	content, err := os.ReadFile(filepath.Join(".", "psw"))
	if err != nil {
		fmt.Printf("%v@%v's password: ", username, hostname)
		fmt.Scan(&password)
		os.WriteFile("./psw", []byte(password), 0644)
	}
	password = string(content)
	return password
}

func copySingleFile(sftpClient *sftp.Client, filename, srcPath, dstPath string) {
	src := srcPath + "/" + filename
	srcFile, err := sftpClient.Open(src)
	if err != nil {
		log.Fatal("Failed to open remote file: ", err)
	}
	defer srcFile.Close()

	dst := filepath.Join(dstPath, filename)
	dst = strings.NewReplacer(":", "_").Replace(dst)
	dstFile, err := os.OpenFile(dst, os.O_RDWR|os.O_CREATE|os.O_TRUNC, 0644)
	if err != nil {
		log.Fatal("Failed to open local file: ", err)
	}
	defer dstFile.Close()

	n, err := io.Copy(dstFile, srcFile)
	if err != nil {
		log.Fatal("Failed to copy file: ", err)
	}
	fmt.Printf("Copied %v: %v\n", FormatBytes(n), filename)

	srcFile.Close()
	if !strings.HasSuffix(src, ".ok") {
		if err := sftpClient.Rename(src, src+".ok"); err != nil {
			log.Fatal("Failed to rename file: ", err)
		}
	}

	dstFile.Close()
	if err := os.Rename(dst, strings.TrimSuffix(dst, ".ok")); err != nil {
		log.Fatal("Failed to rename file: ", err)
	}
}
