package cmd

import (
	"github.com/spf13/cobra"
	"fish-eyes/internal/fissh"
)

var filenameOption  fissh.Option = fissh.Option{Name: fissh.OptionFilename}
var dateOption      fissh.Option = fissh.Option{Name: fissh.OptionDate}
var latestVidOption fissh.Option = fissh.Option{Name: fissh.OptionLatestVid}
var latestPicOption fissh.Option = fissh.Option{Name: fissh.OptionLatestPic}
const defaultDate string = "20240101"

var dstPath string

var getCmd = &cobra.Command{
	Use:   "get",
	Short: "",
	Long: ``,
	Run: func(cmd *cobra.Command, args []string) {
		fissh.ChangeUsername(username)
		switch {
		case filenameOption.Value != "":
			fissh.GetFishMedia(fishID, filenameOption, dstPath)
		case dateOption.Value != "":
			fissh.GetFishMedia(fishID, dateOption, dstPath)
		case latestVidOption.Value != "":
			fissh.GetFishMedia(fishID, latestVidOption, dstPath)
		case latestPicOption.Value != "":
			fissh.GetFishMedia(fishID, latestPicOption, dstPath)
		}
	},
}

func init(){
	rootCmd.AddCommand(getCmd)
	getCmd.Flags().StringVar(&fishID, "id", "", "specify fish id, this is required")
	getCmd.MarkFlagRequired("id")

	getCmd.Flags().StringVarP(&filenameOption.Value, "name", "n", "", "specify the name of file")
	getCmd.Flags().StringVarP(&dateOption.Value, "date", "d", "", "specify file date, ex:" + defaultDate)
	getCmd.Flags().StringVar(&latestVidOption.Value, "latestVid", "", "specify the number of latest vids to get")
	getCmd.Flags().StringVar(&latestPicOption.Value, "latestPic", "", "specify the number of latest pics to get")
	getCmd.MarkFlagsMutuallyExclusive("name", "date", "latestVid", "latestPic")

	getCmd.Flags().StringVar(&dstPath, "path", ".", "specify destination path")
	getCmd.Flags().StringVar(&username, "username", "aifi-fish", "change username")
}
