import csv
from datetime import datetime

# Helper Functions
def format_phone(phone):
    """Format a phone number as (XXX) XXX-XXXX if 10 digits."""
    if not phone:
        return ""
    digits = ''.join(filter(str.isdigit, phone))
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone

def yes_no_to_true_false(value):
    """Convert 'yes'/'no' to 'TRUE'/'FALSE'."""
    if value.lower() == "yes":
        return "TRUE"
    elif value.lower() == "no":
        return "FALSE"
    return ""

def map_grade(grade):
    """Map school grade to a numeric value."""
    if not grade:
        return ""
    grade_lower = grade.lower()
    if "graduated" in grade_lower:
        return ""
    if "pre-school" in grade_lower:
        return -1
    grade_map = {
        "pre-k": -1, "kindergarten": 0, "first grade": 1, "second grade": 2,
        "third grade": 3, "fourth grade": 4, "fifth grade": 5, "sixth grade": 6,
        "seventh grade": 7, "eighth grade": 8, "ninth grade": 9, "tenth grade": 10,
        "eleventh grade": 11, "twelfth grade": 12
    }
    for key, value in grade_map.items():
        if key in grade_lower:
            return value
    try:
        num = int(''.join(filter(str.isdigit, grade)))
        if 1 <= num <= 12:
            return num
    except ValueError:
        return ""

def get_status_and_membership(member_status):
    """Determine Status and Membership based on Member Status."""
    if not member_status or member_status.lower() == "no":
        return "Inactive", ""
    else:
        return "Active", "Member"

def format_birthdate(birth_month_day, age):
    """Format birthdate from MM/DD and age."""
    if not birth_month_day:
        return ""
    try:
        dt = datetime.strptime(birth_month_day, "%m/%d")
        birth_year = current_year - int(age) if age and age.isdigit() else 1885
        return dt.replace(year=birth_year).strftime("%m/%d/%Y")
    except ValueError:
        return ""

def format_anniversary(wedding_month_day):
    """Format anniversary from MM/DD."""
    if not wedding_month_day:
        return ""
    try:
        dt = datetime.strptime(wedding_month_day, "%m/%d")
        return dt.replace(year=1885).strftime("%m/%d/%Y")
    except ValueError:
        return ""

# File paths
input_file = "input.csv"
output_file = "output.csv"

# Define output headers
output_headers = [
    "remote_id", "First Name", "Middle Name", "Last Name",
    "Birthdate", "Anniversary", "Gender", "Grade", "Medical Notes", "Marital Status", "Status", "Membership",
    "Home Address Street Line 1", "Home Address City", "Home Address State", "Home Address Zip Code",
    "Mobile Phone Number", "Home Phone Number", "Work Phone Number",
    "Home Email", "Household ID", "Household Name", "Household Primary Contact",
    "Baptized", "Baptism Date", "Member By", "Membership Date", "Sunday School", "Small Group",
    "Emergency Contact", "Emergency Phone", "Allergies", "Authorized Pickup"
]

# Process CSV
with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=output_headers)
    writer.writeheader()

    family_id = 1
    previous_last_name = None
    remote_id_counter = 1
    current_year = 2025  # Adjust as needed

    for row in reader:
        # Household logic
        last_name = row.get("Last Name", "")
        if last_name and last_name != previous_last_name:
            family_id += 1
            previous_last_name = last_name
        household_id = str(family_id) if last_name else "1"

        # Generate remote_id
        remote_id = str(remote_id_counter)
        remote_id_counter += 1

        # Format dates
        birthdate = format_birthdate(row.get("Birth Month and Day", ""), row.get("Age", ""))
        anniversary = format_anniversary(row.get("Wedding Month and Day", ""))

        # Process medical notes
        medical_notes = row.get("Allergy", "").lower()
        if medical_notes == "no":
            medical_notes = ""

        # Map grade
        grade = map_grade(row.get("School Grade", ""))

        # Format phone numbers
        mobile_phone = format_phone(row.get("Cell Phone", ""))
        home_phone = format_phone(row.get("Home Phone", ""))
        work_phone = format_phone(row.get("Work Phone", ""))

        # Baptized status
        baptized = yes_no_to_true_false(row.get("Baptized", ""))

        # Status and Membership
        status, membership = get_status_and_membership(row.get("Member Status", ""))

        # Authorized pickup
        authorized_pickup = "|".join(filter(None, [row.get(f"Authorized Pick up {i}", "") for i in range(1, 9)]))

        # Household primary contact
        relationship = row.get("Relationship", "")
        household_primary_contact = "TRUE" if relationship == "Head of Household" else "TRUE" if row.get("Primary Contact", "").lower() == "yes" else ""

        # Emergency contact logic
        emergency_contact = row.get("Emergency Contact", "")
        if not emergency_contact:
            primary_contact = row.get("Primary Contact", "")
            first_name = row.get("First Name", "").lower()
            if primary_contact:
                primary_first_name = primary_contact.split()[0].lower() if primary_contact.split() else ""
                if primary_first_name != first_name:
                    emergency_contact = primary_contact
                else:
                    emergency_contact = row.get("Secondary Contact", "")
            else:
                emergency_contact = row.get("Secondary Contact", "")

        # Construct output row
        output_row = {
            "remote_id": remote_id,
            "First Name": row.get("First Name", ""),
            "Middle Name": row.get("Middle Name", ""),
            "Last Name": last_name,
            "Birthdate": birthdate,
            "Anniversary": anniversary,
            "Gender": row.get("Gender", ""),
            "Grade": str(grade) if grade != "" else "",
            "Medical Notes": medical_notes,
            "Marital Status": row.get("Marital Status", ""),
            "Status": status,
            "Membership": membership,
            "Home Address Street Line 1": row.get("Address", ""),
            "Home Address City": row.get("City", ""),
            "Home Address State": row.get("State", ""),
            "Home Address Zip Code": row.get("Zip Code", ""),
            "Mobile Phone Number": mobile_phone,
            "Home Phone Number": home_phone,
            "Work Phone Number": work_phone,
            "Home Email": row.get("E-Mail", ""),
            "Household ID": household_id,
            "Household Name": f"{last_name} Household" if last_name else "",
            "Household Primary Contact": household_primary_contact,
            "Baptized": baptized,
            "Baptism Date": row.get("Baptized Date", ""),
            "Member By": row.get("How Joined", ""),
            "Membership Date": row.get("Date Joined", ""),
            "Sunday School": row.get("Sunday School", ""),
            "Small Group": row.get("Activities", ""),  # Maps Child/Youth Group Activities
            "Emergency Contact": emergency_contact,
            "Emergency Phone": format_phone(row.get("Emergency Phone", "")),
            "Allergies": row.get("Allergy", ""),
            "Authorized Pickup": authorized_pickup
        }
        writer.writerow(output_row)

print(f"CSV transformation complete. Output saved to {output_file}")
