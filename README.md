# Data Set: Finding Unsafe Go Code in the Wild

This is the data set and scripts for our paper "Uncovering the Hidden Dangers: Finding Unsafe Go Code in the Wild".

**Authors:**  
Johannes Lauinger, Lars Baumgärtner, Anna-Katharina Wickert, and Mira Mezini  
Technische Universität Darmstadt, D-64289 Darmstadt, Germany  
E-mail: {baumgaertner, wickert, mezini} (with) cs.tu-darmstadt.de, jlauinger (with) seemoo.tu-darmstadt.de


## Research pipeline

To create and process the data for our study, we used the following pipeline:

 1. Raw projects and dependencies. This set contains the 500 open-source Go projects that we crawled from GitHub.
    The projects at the specific revision that we examined are referenced in this repository through Git submodules.
    The `projects` directory contains the submodules.
 2. Package and unsafe data. From the projects and their dependencies, we compiled the list of all packages used
    transitively. Within all packages, we identified usages of `unsafe` Go code. The results of this stage are
    included in the `data` directory.
 3. We used Python to examine the data and sample 1,400 code snippets for manual classification by unsafe usage type
    and purpose. The results of this stage are included in the `analysis` and `labeled-usages-dataset` directories.


## Directory structure

The directories in this repository contain the following:

 - `analysis` contains the Jupyter notebook with the Python code to reproduce our analysis steps on the data.
 - `data` contains gzipped versions of the CSV files holding project, package, and unsafe code block information,
   as well as the sampled and labeled code snippets.
 - `figures` contains Figures 1 to 5 as included in our paper.
 - `labeled-usages-dataset` contains our data set of labaled usages of unsafe code blocks in Go code. The data set
   is divided into 400 Go standard library usages (std) and 1,000 application code (non-standard library) usages
   (app). Each directory contains subfolders with names similar to `efficiency__cast-struct`, where the purpose
   label and usage label as used in our paper are included, separated by two underscores. Each of the directories
   contains one file for each classified usage, as described in more detail below.
 - `projects` contains Git submodules for each of the 500 projects under examination, set to the specific revision
   that we analyzed.
 - `scrips` contains Python scripts to replicate the figures and tables included in our paper, as well as the
   data acquisition tool that we used to extract unsafe code blocks from the projects and a Jupyter notebook with
   the Python code that we used to explore the data.


## Raw project data: project code and dependencies

We analyzed the 500 top-rated Go projects from GitHub. They are referenced through Git submodules in this repository.
From these, we excluded 150 projecs that did not yet support modules, and 7 which did not compile.

The projects that did not support Go modules can be identified from the `data/projects.csv.gz` file using the
`project_used_modules` column. The projects that did not compile are listed in the `data/projects_with_errors.txt`
file.

To make it easier to fetch the projects in the exact revision we used for reproduction of the study, as well as to
get the correct dependency versions, we provide the projects and dependencies as `tar.gz` compressed archives on the
Zenodo platform: [https://zenodo.org/deposit/3987400](https://zenodo.org/deposit/3987400)


## Data: unsafe code blocks

The `data/geiger_findings_0_499.csv.gz` file contains the unsafe code findings. Each line in the file represents one
finding. It holds the corresponding code line, as +/- 5 lines code context, as well as meta data about the finding.
The meta data includes the line number, column, file, package, module, and project where it was found. Package and
project data is a foreign key to the `data/packages_0_499.csv.gz` and `data/projects.csv.gz` files, respectively,
which provide more detailed information. For example, the packages file contains total finding counts for each
package.

The `data` directory also contains the `sampled_usages_app.csv.gz` and `sampled_usages_std.csv.gz` files, which are
samples subsets of the `geiger_findings_0_499.csv.gz` file containing 1,000 and 400 unique samples together with two
labels for each line.


## Labeled data set of unsafe usages in the wild

As described in our paper, we randomly sampled 1,400 unique unsafe usages from the 10 projects with the most overall
unsafe usages. We then manually classified these samples in two dimensions: by what is being done and for what purpose.

We identified the following classes for the first dimension, what is being done:

 - `cast-struct`, `cast-basic`, `cast-bytes`, `cast-pointer`, `cast-header` (all summarized as `cast` in our paper to
   save space): all kinds of casts between arbitrary types and structs, basic Go types, `[]byte` slices or `[N]byte`
   arrays, actual `unsafe.Pointer` values, or `reflect.SliceHeader` and `reflect.StringHeader` values, respectively.
 - `memory-access`: dereferencing of unsafe pointers, manipulation of referenced memory, or comparison of the actual
   stored addresses.
 - `pointer-arithmetic`: all kinds of arithmetic manipulation of addresses, such as manually advancing a slice.
 - `definition`: groups usages where a field or method of type `unsafe.Pointer` is declared for later usage.
 - `delegate`: instances where unsafe is needed only because another function requires an argument of type `unsafe.Pointer`.
 - `syscall`: groups calls to `syscall.Syscall` or other native syscalls.
 - `unused`: occurences that are not actually being used, e.g. dead code or unused function parameters.

Purpose of usage is labeled with the following classes:

 - `efficiency`: all uses of unsafe to improve time or space complexity, such as in-place casts. Code contained in this class could also be written
   without the use of unsafe, decreasing effeciency.
 - `serialization`: contains marshalling and serialization operations.
 - `generics`: contains usages of unsafe that achieve functionality that could have been written without unsafe if Go provided
   support for generics.
 - `no-gc` (avoid garbage collection): contains usages where unsafe is used to tell the compiler to not free a value until
   a function returns, such as when calling assembly code.
 - `atomic` (atomic operations): contains usages of the atomic package which require unsafe.
 - `ffi` (foreign function interface): contains calls to Cgo or other function interfaces that require unsafe by their contract.
 - `hide-escape`: contains snippets where unsafe is used to hide a value from Go escape analysis.
 - `layout` (memory layout control): contains unsafe usages to achieve low-level memory management, such as precise alignment.
 - `types`: contains unsafe usages needed to implement the Go type system itself. Only present in the `std` samples.
 - `reflect`: contains instances of type reflection and re-implementations of some types from the reflect package,
   such as using `unsafe.Pointer` instead of `uintptr` for slice headers.
 - `unused`: again, contains occurences that are not actually being used.

The `labeled-usages-dataset` is organized as follows: the `app` and `std` contain 1,000 and 400 samples, respectively, divided by
application (non-standard libraries) and standard-library usages. Each of them contains subdirectories grouping the snippets by
their combination of labels. The subdirectories are named similar to `efficiency__cast-struct`. Both labels of the samples are
concatenated using two underscores. Every combination of labels that actually contains samples has its own directory.

The samples are provided as one file for each sample. The file name is a hash of line number, file, package etc. of the finding,
providing a guaranteed unique name. The files contain 4 sections divided by dashes. The first section provides information
about the module, version, package, file, and line of the snippet. It also states which project included this snippet (but
there can be more projects in the data set that share usage of the snippet), and the labels as already included in the directory
name. The information is guaranteed to be in the same line number across files. The second section contains the snippet
code line. The third and fourth section contain a +/- 5 lines and +/- 100 lines context, respectively.

Additionally, the labaled data set is included in machine-readable CSV format in the `data/sampled_usages_app.csv.gz` and
`data/sampled_usaged_std.csv.gz` as described previously.


## How to reproduce figures and tables

To reproduce the figures and tables included in our paper, simply execute the corresponding scripts in the `scripts` directory.
They also provide formal documentation about the specific data analysis that we did:

```
cd scripts
./create-figure-distribution-unsafe-types.py
./create-figure-unsafe-import-depth.py
./create-table-dataset-labels.py
./create-table-dataset-projects.py
```

Figures are saved as PDF files in the same directory, tables are written to the terminal as LaTeX code.

To execute the scripts, you need the following Python libraries:

 - Pandas
 - Numpy
 - Matplotlib
 - Tikzplotlib
 - Seaborn


## How to reproduce the data set

To reproduce the data set, first obtain the raw project code and dependencies. The easiest way to do this is to get the
compressed archive with the exact project code that we used from our Zenodo record:
[https://zenodo.org/deposit/3987400](https://zenodo.org/deposit/3987400)

Alternatively, you can recursively clone this repository to check out the projects data set submodules. The projects
are included as submodules at the correct revision that we used for analysis in this repository. They are located in
the `projects` directory. After recursively cloning the repositories, you may need to run `go mod vendor` in the root
directory of each repository to make sure that all dependencies are properly downloaded. This step is unnecessary when
using the Zenodo record.

Then, build and execute the data acquisition tool in the `scripts/data-acquisition-tool` directory. The folder contains
a README file with the build instructions and usage information.


## License

All project and dependency code is licensed under the terms of the respective licenses for the specific projects.

<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/4.0/"><img alt="Creative Commons Lizenzvertrag" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-nd/4.0/88x31.png" /></a><br />Our study material and data set is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/4.0/">Creative Commons Attribution-NonCommercial-NoDerivs  4.0 International License</a>.

