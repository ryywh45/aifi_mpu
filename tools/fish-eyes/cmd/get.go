package cmd

import (
	"github.com/spf13/cobra"
	"fish-eyes/internal/fissh"
)

var filename string
var dstPath string

var getCmd = &cobra.Command{
	Use:   "get",
	Short: "",
	Long: ``,
	Run: func(cmd *cobra.Command, args []string) {
		fissh.ChangeUsername(username)
		fissh.GetFishMedia(fishID, filename, dstPath)
	},
}

func init(){
	rootCmd.AddCommand(getCmd)
	getCmd.Flags().StringVar(&fishID, "id", "", "specify fish id, this is required")
	getCmd.MarkFlagRequired("id")
	getCmd.Flags().StringVarP(&filename, "name", "n", "", "specify the name of file")
	getCmd.Flags().StringVar(&dstPath, "path", ".", "specify destination path")
	getCmd.Flags().StringVar(&username, "username", "aifi-fish", "change username")
}
