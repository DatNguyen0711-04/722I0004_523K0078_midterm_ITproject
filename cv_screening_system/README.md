# CV Screening System

A CLI-based CV screening system using semantic skill matching powered by sentence-transformers.

## Requirements

- Python 3.10 or higher
- Libraries listed in requirements.txt

## Quick Start

```
cd cv_screening_system
python app.py
```

The system will automatically install missing dependencies on first run.

## How It Works

1. Select a recruitment wave
2. Select the role the candidate applied for
3. Provide the path to the candidate CV (PDF format)
4. The system extracts text from the PDF
5. Semantic similarity is computed between the CV and job description skills
6. A match score is calculated
7. Missing skills are identified
8. The CV is compared against other available roles
9. A recommendation is provided if a better role match is found
10. A report is saved to data/output_reports/

## Project Structure

```
cv_screening_system/
    app.py
    config/
        settings.py
        recruitment_wave.json
    data/
        incoming_cv/
        stored_cv/
        output_reports/
    jd/
        software_engineer.json
        data_analyst.json
        mobile_dev.json
    modules/
        pdf_reader/
            pdf_parser.py
        jd_processing/
            jd_loader.py
            skill_extractor.py
        matching/
            semantic_matcher.py
            scoring.py
        recommendation/
            recommender.py
    utils/
        file_manager.py
        report_writer.py
    requirements.txt
    README.md
```

## Model

Uses the `all-MiniLM-L6-v2` sentence-transformer model for semantic similarity computation.
