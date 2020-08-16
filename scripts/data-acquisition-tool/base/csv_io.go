package base

import (
	"github.com/gocarina/gocsv"
	"os"
)

var packagesFile *os.File
var packagesFileHeaderWritten = false
var geigerFindingsFile *os.File
var geigerFindingsFileHeaderWritten = false
var errorConditionsFile *os.File
var errorConditionsFileHeaderWritten = false

func OpenPackagesFile(packagesFilename string) error {
	var err error
	packagesFile, err = os.OpenFile(packagesFilename, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0644)
	return err
}

func OpenGeigerFindingsFile(geigerFilename string) error {
	var err error
	geigerFindingsFile, err = os.OpenFile(geigerFilename, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0644)
	return err
}

func OpenErrorConditionsFile(errorsFilename string) error {
	var err error
	errorConditionsFile, err = os.OpenFile(errorsFilename, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0644)
	return err
}

func CloseFiles() {
	if packagesFile != nil {
		packagesFile.Close()
	}
	if geigerFindingsFile != nil {
		geigerFindingsFile.Close()
	}
	if errorConditionsFile != nil {
		errorConditionsFile.Close()
	}
}

func ReadProjects(filename string)([]*ProjectData, error) {
	f, err := os.Open(filename)
	if err != nil {
		return []*ProjectData{}, err
	}
	defer f.Close()

	var projects []*ProjectData

	if err := gocsv.UnmarshalFile(f, &projects); err != nil {
		return []*ProjectData{}, err
	}

	return projects, nil
}

func WritePackage(module PackageData) error {
	if packagesFileHeaderWritten {
		return gocsv.MarshalWithoutHeaders([]PackageData{module}, packagesFile)
	} else {
		packagesFileHeaderWritten = true
		return gocsv.Marshal([]PackageData{module}, packagesFile)
	}
}

func WriteGeigerFinding(geigerFinding GeigerFindingData) error {
	if geigerFindingsFileHeaderWritten {
		return gocsv.MarshalWithoutHeaders([]GeigerFindingData{geigerFinding}, geigerFindingsFile)
	} else {
		geigerFindingsFileHeaderWritten = true
		return gocsv.Marshal([]GeigerFindingData{geigerFinding}, geigerFindingsFile)
	}
}

func WriteErrorCondition(errorCondition ErrorConditionData) error {
	if errorConditionsFileHeaderWritten {
		return gocsv.MarshalWithoutHeaders([]ErrorConditionData{errorCondition}, errorConditionsFile)
	} else {
		errorConditionsFileHeaderWritten = true
		return gocsv.Marshal([]ErrorConditionData{errorCondition}, errorConditionsFile)
	}
}
