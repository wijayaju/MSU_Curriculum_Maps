## orphanate.jl usage

### Run from repo root

**Without writing output**

```bash
julia --project=. julia/scripts/orphanate.jl outputs/fake_data_sci_103.csv
```

**With writing output**

```bash
julia --project=. julia/scripts/orphanate.jl outputs/fake_data_sci_103.csv --write
```

---

### Run from another directory

Use full or relative paths:

```bash
julia --project=/path/to/repo /path/to/repo/julia/scripts/orphanate.jl /path/to/repo/outputs/file.csv --write
```

---

### Use inside a notebook (in `notebooks/`)

```julia
include("../julia/scripts/orphanate.jl")

df = orphanate_curriculum("../outputs/fake_data_sci_103.csv")

df2 = orphanate_curriculum("../outputs/fake_data_sci_103.csv"; write_output=true)
```

---

### Optional: run from repo root inside notebook

```julia
cd("..")

include("julia/scripts/orphanate.jl")

df = orphanate_curriculum("outputs/fake_data_sci_103.csv"; write_output=true)
```
