package cmd

import (
	"fmt"
	"github.com/spf13/cobra"
	"github.com/stg-tud/unsafe_go_study_results/scripts/data-acquisition-tool/base"
)

var offset, length int
var skipProjects []string
var doCopy bool
var copyDestination string

var analyzeCmd = &cobra.Command{
	Use:   "analyze",
	Short: "Runs the analysis",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("Use analyze geiger")
	},
}

func init() {
	RootCmd.AddCommand(analyzeCmd)

	analyzeCmd.PersistentFlags().IntVar(&offset, "offset", 0, "parallelization: projects slicing offset")
  analyzeCmd.PersistentFlags().IntVar(&length, "length", base.NoLengthGiven, "parallelization: projects slicing length. Default: projects count")
	analyzeCmd.PersistentFlags().StringArrayVar(&skipProjects, "skip", []string{}, "skip these project names, e.g golang/go")
	analyzeCmd.PersistentFlags().BoolVar(&doCopy, "copy", false, "copy files with vulnerabilities into copy destination")
	analyzeCmd.PersistentFlags().StringVar(&copyDestination, "copy-destination", "", "directory to store copies of vulnerable files in")
}
