package cmd

import (
	"fish-eyes/internal/ui"
	"github.com/spf13/cobra"
)

var uiCmd = &cobra.Command{
	Use:   "ui",
	Short: "",
	Long: ``,
	Run: func(cmd *cobra.Command, args []string) {
		ui.Run()
	},
}

func init(){
	rootCmd.AddCommand(uiCmd)
}
