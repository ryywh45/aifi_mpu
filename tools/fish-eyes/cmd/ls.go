package cmd

import (
	"fmt"
	"github.com/spf13/cobra"
	"fish-eyes/internal/fissh"
)

var fishID string
var vidOnly bool
var picOnly bool
var username string

var lsCmd = &cobra.Command{
	Use:   "ls",
	Short: "List video/picture on specify fish",
	Long: `List video/picture on specify fish`,
	Run: func(cmd *cobra.Command, args []string) {
		fissh.ChangeUsername(username)
		switch {
		case vidOnly:
			fmt.Println(fissh.ListFishMedia(fishID, true, false))
		case picOnly:
			fmt.Println(fissh.ListFishMedia(fishID, false, true))
		default:	
			fmt.Println(fissh.ListFishMedia(fishID, true, true))
		}
	},
}

func init() {
	rootCmd.AddCommand(lsCmd)
	lsCmd.Flags().StringVar(&fishID, "id", "", "specify fish id, this is required")
	lsCmd.MarkFlagRequired("id")
	lsCmd.Flags().BoolVarP(&vidOnly, "vid-only", "v", false, "only list videos")
	lsCmd.Flags().BoolVarP(&picOnly, "pic-only", "p", false, "only list pictures")
	lsCmd.MarkFlagsMutuallyExclusive("vid-only", "pic-only")
	lsCmd.Flags().StringVarP(&username, "username", "n", "aifi-fish", "change username")
}
