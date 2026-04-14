#!/usr/bin/env julia

# orphanate.jl
#
# Purpose:
#   Remove orphan courses from a Curricular Analytics CSV.
#
# A course is removed if it has:
#   - no prerequisites
#   - no corequisites
#   - no strict-corequisites
#   - and is not referenced by any other course in those fields
#
# Input:
#   A Curricular Analytics CSV with metadata rows followed by a course table
#   starting at the row beginning with "Course ID,"
#
# Output:
#   - returns a filtered DataFrame
#   - optionally writes outputs/ORPH_<original_filename>.csv

using CSV
using DataFrames

function parse_relation_ids(value)
    if ismissing(value)
        return Int[]
    end

    s = strip(string(value))
    isempty(s) && return Int[]

    ids = Int[]
    for part in split(s, ';')
        p = strip(part)
        isempty(p) && continue
        try
            push!(ids, parse(Int, p))
        catch
            @warn "Skipping invalid relationship ID: $p"
        end
    end
    return ids
end

function is_empty_relation(value)
    ismissing(value) || isempty(strip(string(value)))
end

function read_ca_csv(filepath::AbstractString)
    lines = readlines(filepath)

    header_idx = findfirst(line -> startswith(line, "Course ID,"), lines)
    isnothing(header_idx) && error("Could not find course table header.")

    header_lines = lines[1:header_idx]

    header_line = lines[header_idx]
    expected_commas = count(==(','), header_line)

    table_lines = [
        line for line in lines[header_idx:end]
        if count(==(','), line) == expected_commas
    ]

    io = IOBuffer(join(table_lines, "\n"))
    df = CSV.read(io, DataFrame)

    return header_lines, df
end

function write_ca_csv(filepath::AbstractString, header_lines::Vector{String}, df::DataFrame)
    open(filepath, "w") do io
        for line in header_lines
            println(io, line)
        end
    end

    CSV.write(filepath, df; append=true, writeheader=false)
end

function orphanate_curriculum(
    filepath::AbstractString;
    write_output::Bool=false,
    output_dir::Union{Nothing,AbstractString}=nothing,
    verbose::Bool=true
)
    header_lines, df = read_ca_csv(filepath)

    required_cols = ["Course ID", "Prerequisites", "Corequisites", "Strict-Corequisites"]
    missing_cols = [c for c in required_cols if !(c in names(df))]
    !isempty(missing_cols) && error("Missing required columns: $(join(missing_cols, ", "))")

    relation_cols = ["Prerequisites", "Corequisites", "Strict-Corequisites"]
    referenced_ids = Set{Int}()

    for row in eachrow(df), col in relation_cols
        for id in parse_relation_ids(row[col])
            push!(referenced_ids, id)
        end
    end

    keep_mask = Vector{Bool}(undef, nrow(df))

    for (i, row) in enumerate(eachrow(df))
        course_id = try
            Int(row["Course ID"])
        catch
            error("Invalid Course ID at row $i: $(row["Course ID"])")
        end

        has_outgoing = any(!is_empty_relation(row[col]) for col in relation_cols)
        has_incoming = course_id in referenced_ids

        keep_mask[i] = has_outgoing || has_incoming
    end

    filtered_df = df[keep_mask, :]

    if verbose
        removed = nrow(df) - nrow(filtered_df)
        println("Original course count: $(nrow(df))")
        println("Filtered course count: $(nrow(filtered_df))")
        println("Removed orphaned courses: $removed")
    end

    if write_output
        if isnothing(output_dir)
            repo_root = normpath(joinpath(@__DIR__, "..", ".."))
            output_dir = joinpath(repo_root, "outputs")
        end

        mkpath(output_dir)
        outfile = joinpath(output_dir, "ORPH_" * basename(filepath))
        write_ca_csv(outfile, header_lines, filtered_df)

        if verbose
            println("Wrote orphan-filtered curriculum to:")
            println(outfile)
        end
    end

    return filtered_df
end

function print_usage()
    println("""
Usage:
    julia --project=. julia/scripts/orphanate.jl <input_csv> [--write]

Options:
    --write    Write output to outputs/ORPH_<input_filename>.csv
""")
end

function main()
    isempty(ARGS) && return print_usage()

    input_csv = ARGS[1]
    write_output = "--write" in ARGS

    orphanate_curriculum(input_csv; write_output=write_output, verbose=true)
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end