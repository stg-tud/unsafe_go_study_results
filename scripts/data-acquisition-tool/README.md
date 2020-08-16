# Data Acquisition Tool

## Usage

```shell script
go build
mkdir -p /path/to/data/{analysis,classification,geiger}
mkdir -p /path/to/repositories
```

Download repositories:

```shell script
./acquisition projects --download --data-dir=/path/to/data --destination=/path/to/repositories
```

Run analysis.

```shell script
./acquisition analyze geiger --data-dir=/path/to/data
```

To do better parallelization, you can split the analysis into buckets. Not specifying offset and length assumes their
defaults 0 and 500.

```shell script
./acquisition analyze geiger --offset 350 --length 50--data-dir=/path/to/data
```

You can skip projects with the skip argument. It can be applied multiple times.

```shell script
./acquisition analyze geiger --data-dir=/path/to/data --skip golang/go --skip avelino/awesome-go
```

