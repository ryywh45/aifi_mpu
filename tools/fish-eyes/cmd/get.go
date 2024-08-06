package cmd

import (
	"github.com/spf13/cobra"
	"fish-eyes/internal/fissh"
)

var filenameOption  fissh.Option = fissh.Option{Type: fissh.OptionFilename}
var dateOption      fissh.Option = fissh.Option{Type: fissh.OptionDate}
var latestVidOption fissh.Option = fissh.Option{Type: fissh.OptionLatestVid}
var latestPicOption fissh.Option = fissh.Option{Type: fissh.OptionLatestPic}
var taggedOption    fissh.Option = fissh.Option{Type: fissh.OptionTagged} 
var unTaggedOption  fissh.Option = fissh.Option{Type: fissh.OptionUnTagged}

const defaultDate string = "20240101"

var dstPath string

var getCmd = &cobra.Command{
	Use: "get",
	Short: "get specified files on fish",
	Long: `get specified files on fish`,
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

var allCmd = &cobra.Command{
	Use: "all",
	Short: "get all files on fish",
	Long: `get all files on fish`,
	Run: func(cmd *cobra.Command, args []string) {
		fissh.ChangeUsername(username)
		switch {
		case taggedOption.BoolValue:
			fissh.GetFishMedia(fishID, taggedOption, dstPath)
		case unTaggedOption.BoolValue:
			fissh.GetFishMedia(fishID, unTaggedOption, dstPath)
		default:
			fissh.GetFishMedia(fishID, fissh.Option{Type: fissh.OptionAll}, dstPath)
		}
	},
}

func init(){
	rootCmd.AddCommand(getCmd)
	getCmd.Flags().StringVar(&fishID, "id", "", "specify fish id, this is required")
	getCmd.MarkFlagRequired("id")
	allCmd.Flags().StringVar(&fishID, "id", "", "specify fish id, this is required")
	allCmd.MarkFlagRequired("id")

	getCmd.Flags().StringVarP(&filenameOption.Value, "name", "n", "", "specify the name of file")
	getCmd.Flags().StringVarP(&dateOption.Value, "date", "d", "", "specify file date, ex:" + defaultDate)
	getCmd.Flags().StringVar(&latestVidOption.Value, "latestVid", "", "specify the number of latest vids to get")
	getCmd.Flags().StringVar(&latestPicOption.Value, "latestPic", "", "specify the number of latest pics to get")
	getCmd.MarkFlagsMutuallyExclusive("name", "date", "latestVid", "latestPic")

	getCmd.AddCommand(allCmd)
	allCmd.Flags().BoolVar(&taggedOption.BoolValue, "tagged", false, "get all tagged file")
	allCmd.Flags().BoolVar(&unTaggedOption.BoolValue, "untagged", false, "get all untagged file")
	allCmd.MarkFlagsMutuallyExclusive("tagged", "untagged")

	getCmd.Flags().StringVar(&dstPath, "path", ".", "specify destination path")
	getCmd.Flags().StringVar(&username, "username", "aifi-fish", "change username")
	allCmd.Flags().StringVar(&dstPath, "path", ".", "specify destination path")
	allCmd.Flags().StringVar(&username, "username", "aifi-fish", "change username")
}
