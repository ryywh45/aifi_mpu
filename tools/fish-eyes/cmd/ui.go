package cmd

import (
	"fish-eyes/internal/ui"
	"github.com/spf13/cobra"
)

var uiCmd = &cobra.Command{
	Use:   "ui",
	Short: "show a simple ui of application",
	Long: `show a simple ui of application`,
	Run: func(cmd *cobra.Command, args []string) {
		ui.Run()
	},
}

func init(){
	rootCmd.AddCommand(uiCmd)
}
