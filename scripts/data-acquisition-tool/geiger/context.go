package geiger

import (
	"github.com/stg-tud/unsafe_go_study_results/scripts/data-acquisition-tool/base"
	"go/ast"
	"golang.org/x/tools/go/packages"
	"io/ioutil"
	"strings"
)

func getCodeContext(parsedPkg *packages.Package, n ast.Node) (string, string) {
	nodePosition := parsedPkg.Fset.File(n.Pos()).Position(n.Pos())
	lineNumber := nodePosition.Line  // 1-based
	filename := nodePosition.Filename

	fileData, err := ioutil.ReadFile(filename)
	if err != nil {
		panic(err)
	}
	fileLines := strings.Split(string(fileData), "\n")

	if lineNumber > len(fileLines) {
		return "invalid-line-number", "invalid-line-number"
	}

	startLine := base.Max(1, lineNumber - 5)
	endLine := base.Min(len(fileLines), lineNumber + 6)

	text := strings.Trim(fileLines[lineNumber-1], "\n\t")
	context := strings.Join(fileLines[startLine-1:endLine-1], "\n")

	return text, context
}
