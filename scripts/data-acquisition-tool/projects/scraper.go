package projects

import (
	"context"
	"fmt"
	"github.com/go-git/go-git/v5"
	"github.com/gocarina/gocsv"
	"github.com/google/go-github/github"
	"github.com/stg-tud/unsafe_go_study_results/scripts/data-acquisition-tool/base"
	"golang.org/x/oauth2"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

func GetProjects(datasetSize int, dataDir, downloadDir string, download, createForks bool, accessToken string) {
	projectsFilename := fmt.Sprintf("%s/projects.csv", dataDir)

	fmt.Printf("Saving project data to %s\n", projectsFilename)

	headerWritten := false
	projectsFile, err := os.OpenFile(projectsFilename, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0644)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	defer projectsFile.Close()

	fmt.Println("Getting information about top 500 Go projects...")

	ts := oauth2.StaticTokenSource(
		&oauth2.Token{AccessToken: accessToken},
	)
	tc := oauth2.NewClient(context.Background(), ts)
	client := github.NewClient(tc)

	// split up the projects into pages of 100 each because Github's rate limiting does not allow more
	pages := datasetSize / 100
	for page := 1; page <= pages + 1; page++ {
		// calculate the size of this page, if needed at all
		pageSize := base.Min(datasetSize - ((page-1)*100), 100)
		if pageSize <= 0 {
			continue
    }

		// search for repositories with language Go on Github. They are ordered by stars automatically
		repos, _, err := client.Search.Repositories(context.Background(), "language:Go", &github.SearchOptions{
			ListOptions: github.ListOptions{
				PerPage: pageSize,
				Page: page,
			},
		})
		if err != nil {
			fmt.Printf("Error: %v\n", err)
			return
		}

		for i, repo := range repos.Repositories {
			path := downloadDir + "/" + repo.GetFullName()
			revision := ""

			fmt.Printf("%v. %v\n", (page-1)*100+(i+1), *repo.CloneURL)

			if download {
				revision = downloadRepo(repo, path)
			}

			if createForks {
				createFork(client, repo)
			}

			project := base.ProjectData{
				Rank:           (page-1)*100+(i+1),
				Name:           repo.GetFullName(),
				GithubCloneUrl: repo.GetCloneURL(),
				NumberOfStars:  repo.GetStargazersCount(),
				NumberOfForks:  repo.GetForksCount(),
				GithubId:       *repo.ID,
				Revision:       revision,
				CreatedAt:      base.DateTime{Time: repo.CreatedAt.Time},
				LastPushedAt:   base.DateTime{Time: repo.PushedAt.Time},
				UpdatedAt:      base.DateTime{Time: repo.UpdatedAt.Time},
				Size:           *repo.Size,
				CheckoutPath:   path,
			}

			if headerWritten {
				_ = gocsv.MarshalWithoutHeaders([]base.ProjectData{project}, projectsFile)
			} else {
				headerWritten = true
				_ = gocsv.Marshal([]base.ProjectData{project}, projectsFile)
			}
		}
	}
}

func createFork(client *github.Client, repo github.Repository) {
	components := strings.Split(repo.GetFullName(), "/")
	owner := components[0]

	_, _, err := client.Repositories.CreateFork(context.Background(), owner, *repo.Name,
		&github.RepositoryCreateForkOptions{})
	_, ok := err.(*github.AcceptedError)
	if !ok && err != nil {
		fmt.Printf("ERROR: %v!", err)
	}

	fmt.Printf("  forked to %s\n", *repo.Name)
}

func downloadRepo(repo github.Repository, path string) string {
	fmt.Printf("  Downloading to %v ...", path)

	cloneCtx, err := git.PlainClone(path, false, &git.CloneOptions{
		URL:               *repo.CloneURL,
		Depth:             1,
		Progress:          nil,
	})

	if err != nil {
		fmt.Printf("ERROR: %v!\n", err)
	} else {
		fmt.Println("done")
	}

	fmt.Printf("  Vendoring Go modules ...")

	var goModPaths []string

	err = filepath.Walk(path, func(path string, info os.FileInfo, err error) error {
		if err == nil && strings.ToLower(info.Name()) == "go.mod" {
			goModPaths = append(goModPaths, path[:len(path)-len("go.mod")])
		}
		return nil
	})
	if err != nil {
		fmt.Printf("ERROR: %v!\n", err)
	}

	for _, goModPath := range goModPaths {
		fmt.Printf("\n  Running go mod vendor in %v ...", goModPath)

		cmd := exec.Command("go", "mod", "vendor")
		cmd.Dir = goModPath

		err = cmd.Run()

		if err != nil {
			fmt.Printf("ERROR: %v!", err)
		} else {
			fmt.Printf("done")
		}
	}

	head, err := cloneCtx.Head()
	if err != nil {
		fmt.Printf("ERROR: %v!", err)
	}
	revision := head.Hash().String()

	fmt.Printf("\n  done with revision %s\n", revision)

	return revision
}
