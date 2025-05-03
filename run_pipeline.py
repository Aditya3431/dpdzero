import os
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Run the full data pipeline and generate a Slack-style report."
    )
    parser.add_argument(
        "--input_folder",
        type=str,
        required=True,
        help="Path to the folder containing your input CSV files."
    )
    args = parser.parse_args()

    # Step 1: Data Ingestion
    print("🔄 Running Data Ingestion...")
    subprocess.run([
        "python", "-m", "src.data.data_ingestion",
        "--input_folder", args.input_folder,
        "--output_folder", "data/loaded"
    ], check=True)

    # Step 2: Data Validation
    print("🔄 Running Data Validation...")
    subprocess.run([
        "python", "-m", "src.data.data_validation",
        "--data_folder", "data/loaded",
        "--output_folder", "data/validated"
    ], check=True)

    # Step 3: Data Merge
    print("🔄 Running Data Merge...")
    subprocess.run([
        "python", "-m", "src.data.data_merger"
    ], check=True)

    # Step 4: Feature Engineering
    print("🔄 Running Feature Engineering...")
    subprocess.run([
        "python", "-m", "src.data.feature_eng"
    ], check=True)

    # Step 5: Generate Report
    print("✅ Pipeline complete! Now generating report.")
    print("Please enter the date for the report in YYYY-MM-DD format (e.g., 2025-04-28):")
    subprocess.run([
        "python", "-m", "src.summary.report_genrator"
    ])

if __name__ == "__main__":
    main()