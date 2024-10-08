package cmd

import (
	"fmt"
	"log"
	"github.com/spf13/cobra"
	"fish-eyes/internal/frpc"
)

var statusCmd = &cobra.Command{
	Use:   "status",
	Short: "Show a status of frpc on fish",
	Long: `Show a status of frpc on fish`,
	Run: func(cmd *cobra.Command, args []string) {
		infos, err := frpc.GetFrpcInfo()
		if err != nil {
			log.Fatal("Failed to get frpc info: ", err)
		}
		for _, info := range infos {
			fmt.Printf("[ %v ]: ", info.Name)
			switch info.Status {
			case "online":
				fmt.Printf("%v", info.Status)
			case "offline":
				fmt.Printf("%v", info.Status)
			}
			switch {
			case info.Conf.RemotePort != 0:
				fmt.Printf(", %v\n", info.Conf.RemotePort)
			default:
				fmt.Print("\n")
			}
		}
	},
}

func init() {
	rootCmd.AddCommand(statusCmd)
}
