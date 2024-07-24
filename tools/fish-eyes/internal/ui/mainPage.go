package ui

import (
	"fmt"
	"log"

	"fish-eyes/internal/frpc"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/bubbles/table"
	"github.com/charmbracelet/bubbles/spinner"
	"github.com/charmbracelet/lipgloss"
)

const title string = `
 _____ _     _                                
|  ___(_)___| |__         ___ _   _  ___  ___ 
| |_  | / __| '_ \ _____ / _ \ | | |/ _ \/ __|
|  _| | \__ \ | | |_____|  __/ |_| |  __/\__ \
|_|   |_|___/_| |_|      \___|\__, |\___||___/
                              |___/           
`

var (
	tableStyle = lipgloss.NewStyle().
		BorderStyle(lipgloss.NormalBorder()).
		BorderForeground(lipgloss.Color("240"))
	bottonStyle = lipgloss.NewStyle().
		Width(10).Height(1).
		Align(lipgloss.Center, lipgloss.Center).
		BorderStyle(lipgloss.NormalBorder()).
		BorderForeground(lipgloss.Color("240"))
)

type mainModel struct {
	frpcTable table.Model
	tableLoaded bool
	spinner spinner.Model
	width  int
	height int
}

func initialModel() mainModel {
	s := spinner.New()
	s.Spinner = spinner.Line
	// s.Style = lipgloss.NewStyle().Foreground(lipgloss.Color("205"))
	return mainModel{spinner: s}
}

func (m mainModel) Init() tea.Cmd {
	return tea.Batch(tea.EnterAltScreen, createFrpcTable, m.spinner.Tick)
}

func (m mainModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmd tea.Cmd
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "q", "ctrl+c":
			return m, tea.Quit
		}
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
	case table.Model:
		m.frpcTable = msg
		m.tableLoaded = true
	default:
		m.spinner, cmd = m.spinner.Update(msg)
		return m, cmd
	}
	m.frpcTable, cmd = m.frpcTable.Update(msg)
	return m, cmd
}

func (m mainModel) View() string {
	return lipgloss.Place(
		m.width, m.height, 
		lipgloss.Center, lipgloss.Center, 
		lipgloss.JoinVertical(
			lipgloss.Center,
			m.titleView(),
			m.bodyView(),
		),
	)
}

func (m mainModel) titleView() string {
	return title
}

func (m mainModel) bodyView() string {
	var table string
	if m.tableLoaded {
		table = tableStyle.Render(m.frpcTable.View())
	} else {
		table = m.tableLoadingView()
	}

	return lipgloss.JoinHorizontal(
		lipgloss.Top,
		table,
		lipgloss.JoinVertical(
			0,
			bottonStyle.Render("ls   (l)"),
			bottonStyle.Render("get  (g)"),
			bottonStyle.Render("quit (q)"),
		),
	)
}

func (m mainModel) tableLoadingView() string {
	str := fmt.Sprintf("%s Loading frp client info...", m.spinner.View())
	return tableStyle.Render(
		lipgloss.Place(51, 12, lipgloss.Center, lipgloss.Center, str),
	)
}

func createFrpcTable() tea.Msg {
	infos, err := frpc.GetFrpcInfoSlice()
	if err != nil {
		log.Fatal(err)
	}

	columns := []table.Column{
		{Title: "Name", Width: 30},
		{Title: "Status", Width: 10},
		{Title: "Port", Width: 5},
	}

	var rows []table.Row
	for _, info := range infos {
		rows = append(rows, table.Row(info))
	}

	t := table.New(
		table.WithColumns(columns),
		table.WithRows(rows),
		table.WithFocused(true),
		table.WithHeight(10),
	)

	s := table.DefaultStyles()
	s.Header = s.Header.
		BorderStyle(lipgloss.NormalBorder()).
		BorderForeground(lipgloss.Color("240")).
		BorderBottom(true).
		Bold(false)

	s.Selected = s.Selected.
		Foreground(lipgloss.Color("229")).
		Background(lipgloss.Color("25")).
		Bold(false)
	t.SetStyles(s)

	return t
}
