using CSV
using DataFrames

function analyze_courses(csv_filepath::String)
    println("Loading data from $csv_filepath...")
    df = CSV.read(csv_filepath, DataFrame)
    
    println("\nData loaded successfully! Type 'quit' at any prompt to exit.")
    
    function safe_num(x)
        if ismissing(x) return nothing end
        if x isa Number return Float64(x) end
        return tryparse(Float64, strip(string(x)))
    end
    
    function calc_stats(df_subset, dfw_cols)
        avg_grades = safe_num.(df_subset.average_grade)
        tot_grades = safe_num.(df_subset.total_grades)
        
        valid_mask = .!isnothing.(avg_grades) .& .!isnothing.(tot_grades)
        
        if any(valid_mask)
            total_gpa_students = sum(tot_grades[valid_mask])
            gpa = sum(avg_grades[valid_mask] .* tot_grades[valid_mask]) / total_gpa_students
        else
            gpa = NaN
        end
        
        total_dfw = 0.0
        for col in dfw_cols
            col_vals = safe_num.(df_subset[!, col])
            total_dfw += sum([isnothing(x) ? 0.0 : x for x in col_vals])
        end
        
        students = sum([isnothing(x) ? 0.0 : x for x in tot_grades])
        dfw_rate = students > 0 ? (total_dfw / students) * 100 : 0.0
        
        return round(Int, students), gpa, dfw_rate
    end
    
    # --- MAIN INTERACTIVE LOOP ---
    while true
        print("\nEnter Subject Code (e.g., CSE): ")
        subject_code = uppercase(strip(readline()))
        if subject_code == "QUIT" break end
        
        print("Enter Course Code (e.g., 231): ")
        course_code = uppercase(strip(readline()))
        if course_code == "QUIT" break end
        
        course_df = subset(df, 
            :subject_code => ByRow(x -> !ismissing(x) && uppercase(strip(string(x))) == subject_code),
            :course_code => ByRow(x -> !ismissing(x) && uppercase(strip(string(x))) == course_code)
        )
        
        if nrow(course_df) == 0
            println("\nNo data found for $subject_code $course_code.")
            continue
        end
        
        dfw_columns = ["1.5", "1", "0", "D+", "D", "D-", "F", "withdrawn", "late_drop"]
        available_dfw_cols = intersect(dfw_columns, names(course_df))
        
        #OVERALL STATS
        total_students, overall_gpa, overall_dfw = calc_stats(course_df, available_dfw_cols)
        
        println("\n" * "="^65)
        println("OVERALL RESULTS FOR $subject_code $course_code")
        println("="^65)
        println("Total Sections Analyzed : ", nrow(course_df))
        println("Total Students          : ", total_students)
        println("Average GPA (Weighted)  : ", isnan(overall_gpa) ? "N/A" : round(overall_gpa, digits=3))
        println("DFW Rate                : ", round(overall_dfw, digits=1), "%")
        
        #LAST 6 SEMESTERS STATS
        println("\nRECENT SEMESTER TRENDS (Last 6):")
        println("-"^65)
        
        unique_terms = unique(course_df[:, [:term_code, :numeric_term_code]])
        sort!(unique_terms, :numeric_term_code, rev=true)
        
        recent_terms = unique_terms.term_code[1:min(6, end)]
        
        for term in recent_terms
            term_df = subset(course_df, :term_code => ByRow(==(term)))
            stu, gpa, dfw = calc_stats(term_df, available_dfw_cols)
            
            gpa_str = isnan(gpa) ? "N/A" : string(round(gpa, digits=2))
            dfw_str = string(round(dfw, digits=1), "%")
            
            println(rpad(term, 20), "| Students: ", rpad(stu, 6), "| GPA: ", rpad(gpa_str, 5), "| DFW: ", dfw_str)
        end

        println("\nPER-PROFESSOR BREAKDOWN:")
        println("-"^65)
        
        prof_groups = groupby(course_df, :instructors)
        
        for prof_df in prof_groups
            prof_name = first(prof_df.instructors)
            if ismissing(prof_name) 
                prof_name = "Unknown/TBA" 
            end
            
            stu, gpa, dfw = calc_stats(prof_df, available_dfw_cols)            
            if stu == 0 continue end 
            
            gpa_str = isnan(gpa) ? "N/A" : string(round(gpa, digits=2))
            dfw_str = string(round(dfw, digits=1), "%")
            
            println(rpad(prof_name, 30), "| Students: ", rpad(stu, 6), "| GPA: ", rpad(gpa_str, 5), "| DFW: ", dfw_str)
        end
        println("="^65)
    end
end