package cmd

import (
	"github.com/spf13/cobra"
	"github.com/stg-tud/unsafe_go_study_results/scripts/data-acquisition-tool/analysis"
)

var GeigerCmd = &cobra.Command{
	Use:   "geiger",
	Short: "run evaluation with go-geiger implementation",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		analysis.RunAnalysisGeiger(dataDir, offset, length, skipProjects)
	},
}

func init() {
	analyzeCmd.AddCommand(GeigerCmd)
}
