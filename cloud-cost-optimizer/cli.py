import json
import os
from analysis.cost_analyzer import analyze_costs
from llm.extractor import extract_project_profile, InvalidLLMResponse
from billing.generator import generate_mock_billing
from analysis.optimizer import generate_optimization_report


DATA_DIR = "data"
DESCRIPTION_FILE = os.path.join(DATA_DIR, "project_description.txt")
PROFILE_FILE = os.path.join(DATA_DIR, "project_profile.json")
BILLING_FILE = os.path.join(DATA_DIR, "mock_billing.json")
REPORT_FILE = os.path.join(DATA_DIR, "cost_optimization_report.json")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


# ---------------- MENU ACTIONS ----------------

def enter_project_description():
    print("\nEnter project description (end with empty line):\n")

    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)

    description = "\n".join(lines)

    if not description:
        print("❌ Description cannot be empty")
        return

    with open(DESCRIPTION_FILE, "w") as f:
        f.write(description)

    print("✅ Project description saved")


def run_complete_pipeline():
    try:
        with open(DESCRIPTION_FILE) as f:
            description = f.read()
    except FileNotFoundError:
        print("❌ No project description found. Please enter one first.")
        return

    # Step 1: Profile Extraction
    print("\n🔹 Extracting project profile...")
    try:
        profile = extract_project_profile(description)
        with open(PROFILE_FILE, "w") as f:
            json.dump(profile, f, indent=2)
        print("✅ Project profile generated")
    except InvalidLLMResponse as e:
        print("❌ Invalid LLM response during profile extraction")
        print(e)
        return

    # Step 2: Billing Generation
    print("\n🔹 Generating mock billing...")
    try:
        billing = generate_mock_billing(profile)
        with open(BILLING_FILE, "w") as f:
            json.dump(billing, f, indent=2)
        print(f"✅ Generated {len(billing)} billing records")
    except Exception as e:
        print("❌ Billing generation failed")
        print(e)
        return

    # Step 3: Cost Analysis & Recommendations
    analysis = analyze_costs(
        billing_records=billing,
        budget=profile["budget_inr_per_month"]
    )

    print("\n🔹 Generating cost optimization report...")
    try:
        report = generate_optimization_report(profile, billing, analysis)
        with open(REPORT_FILE, "w") as f:
            json.dump(report, f, indent=2)

        print("✅ Cost optimization report generated")
        print(f"💰 Potential Savings: ₹{report['summary']['total_potential_savings']}")
    except Exception as e:
        print("❌ Cost analysis failed")
        print(e)
        return


def view_recommendations():
    try:
        with open(REPORT_FILE) as f:
            report = json.load(f)
    except FileNotFoundError:
        print("❌ No report found. Run analysis first.")
        return

    print("\n📌 Recommendations:\n")
    for i, rec in enumerate(report["recommendations"], start=1):
        print(f"{i}. {rec['title']}")
        print(f"   Service: {rec['service']}")
        print(f"   Savings: ₹{rec['potential_savings']}")
        print(f"   Risk: {rec['risk_level']}")
        print("-" * 50)


def export_report():
    try:
        with open(REPORT_FILE) as f:
            report = json.load(f)
    except FileNotFoundError:
        print("❌ No report to export")
        return

    path = input("Enter export file path (e.g. report.json): ").strip()
    if not path:
        print("❌ Invalid file path")
        return

    with open(path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"✅ Report exported to {path}")


# ---------------- MAIN MENU ----------------

def main():
    ensure_data_dir()

    while True:
        print("""
==============================
 Cloud Cost Optimizer CLI
==============================
1. Enter new project description
2. Run complete cost analysis
3. View recommendations
4. Export report
5. Exit
""")

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            enter_project_description()
        elif choice == "2":
            run_complete_pipeline()
        elif choice == "3":
            view_recommendations()
        elif choice == "4":
            export_report()
        elif choice == "5":
            print("👋 Exiting. Goodbye!")
            break
        else:
            print("❌ Invalid option. Try again.")


if __name__ == "__main__":
    main()
