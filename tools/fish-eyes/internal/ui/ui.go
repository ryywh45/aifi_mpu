package ui

import (
	"fmt"
	"os"

	tea "github.com/charmbracelet/bubbletea"
)


func Run() {
	if _, err := tea.NewProgram(initialModel()).Run(); err != nil {
		fmt.Println("Error running program:", err)
		os.Exit(1)
	}
}
