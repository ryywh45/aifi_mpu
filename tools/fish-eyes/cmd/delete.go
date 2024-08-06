package cmd

import (
	"log"
	"github.com/spf13/cobra"
	"fish-eyes/internal/fissh"
)

var delTaggedOption    fissh.Option = fissh.Option{Type: fissh.OptionDelTagged} 
var delUnTaggedOption  fissh.Option = fissh.Option{Type: fissh.OptionDelUnTagged}

var deleteCmd = &cobra.Command{
	Use: "delete",
	Short: "delete specified files on fish",
	Long: `delete specified files on fish`,
	// Run: func(cmd *cobra.Command, args []string) {
	// },
}

var allDelCmd = &cobra.Command{
	Use: "all",
	Short: "delete all vids/pics on fish",
	Long: `delete all vids/pics on fish`,
	Run: func(cmd *cobra.Command, args []string) {
		fissh.ChangeUsername(username)
		switch {
		case delTaggedOption.BoolValue:
			fissh.DelFishMedia(fishID, delTaggedOption)
		case delUnTaggedOption.BoolValue:
			fissh.DelFishMedia(fishID, delUnTaggedOption)
		default:
			fissh.DelFishMedia(fishID, fissh.Option{Type: fissh.OptionDelAll})
		}
		log.Println("Successfully deleted")
	},
}

func init(){
	rootCmd.AddCommand(deleteCmd)
	deleteCmd.AddCommand(allDelCmd)

	allDelCmd.Flags().StringVar(&fishID, "id", "", "specify fish id, this is required")
	allDelCmd.MarkFlagRequired("id")
	allDelCmd.Flags().StringVar(&username, "username", "aifi-fish", "change username")

	allDelCmd.Flags().BoolVar(&delTaggedOption.BoolValue, "tagged", false, "delete all tagged file")
	allDelCmd.Flags().BoolVar(&delUnTaggedOption.BoolValue, "untagged", false, "delete all untagged file")
	allDelCmd.MarkFlagsMutuallyExclusive("tagged", "untagged")
}
