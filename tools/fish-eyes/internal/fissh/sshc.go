package fissh

import (
	"fmt"
	"net"
	"log"
	"os"
	"runtime"
	"path/filepath"

	"golang.org/x/crypto/ssh"
	"golang.org/x/crypto/ssh/agent"
)

var hostname string
var username string = "aifi-fish"

func Connect(port string) (*ssh.Client, error) {
	askHostname()
	config := &ssh.ClientConfig{
		User: username,
		HostKeyCallback: ssh.InsecureIgnoreHostKey(),
	}

	conn, err := net.Dial("unix", os.Getenv("SSH_AUTH_SOCK"))
	if err != nil {
		log.Fatalf("Failed to open SSH_AUTH_SOCK: %v", err)
	}

	agentClient := agent.NewClient(conn)
	config.Auth = []ssh.AuthMethod{ ssh.PublicKeysCallback(agentClient.Signers) }

	// signer, err := loadPrivateKey()
	// if err != nil {	
	// 	fmt.Println(err)
	// 	config.Auth = []ssh.AuthMethod{ ssh.Password(askPassword()) }
	// } else {
	// 	config.Auth = []ssh.AuthMethod{ ssh.PublicKeys(signer) }	
	// }

	addr := hostname + ":" + port
	client, err := ssh.Dial("tcp", addr, config)
	if err != nil {
		config.Auth = []ssh.AuthMethod{ ssh.Password(askPassword()) }
		client, err = ssh.Dial("tcp", addr, config)
		if err != nil {
			return nil, fmt.Errorf("unable to connect to fish: %v", err)
		}
	}

	return client, nil
}

func ChangeUsername(name string) {
	username = name
}

func askHostname() {
	content, err := os.ReadFile("./host")
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
	fmt.Printf("%v@%v's password: ", username, hostname)
	fmt.Scan(&password)
	return password
}

func checkPrivateKeyPath() string {
	privateKeyPath := ""
    switch runtime.GOOS {
    case "windows":
        privateKeyPath = filepath.Join(os.Getenv("USERPROFILE"), ".ssh", "id_rsa")
    case "linux", "darwin":
        privateKeyPath = filepath.Join(os.Getenv("HOME"), ".ssh", "id_rsa")
    }
	return privateKeyPath
}

func loadPrivateKey() (ssh.Signer, error) {
	privateKeyPath := checkPrivateKeyPath()

	key, err := os.ReadFile(privateKeyPath)
	if err != nil {
		return nil, fmt.Errorf("unable to read private key: %v", err)
	}

	signer, err := ssh.ParsePrivateKey(key)
	if err != nil {
		return nil, fmt.Errorf("unable to parse private key: %v", err)
	}

	return signer, nil
}
