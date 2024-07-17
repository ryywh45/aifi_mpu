package cmd

import (
	"os"
	"github.com/spf13/cobra"
)

var hostname string

var setCmd = &cobra.Command{
	Use:   "set",
	Short: "",
	Long: ``,
	Run: func(cmd *cobra.Command, args []string) {
		if hostname != "" {
			os.WriteFile("./host", []byte(hostname), 0644)
		}
	},
}

func init(){
	rootCmd.AddCommand(setCmd)
	setCmd.Flags().StringVar(&hostname, "hostname", "", "ask author to get hostname")
}
