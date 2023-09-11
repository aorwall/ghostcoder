def format_employee_data(employee_data):
    # Handle edge case of empty input
    if not employee_data:
        return []

    # Sort the data
    sorted_data = sorted(employee_data, key=lambda x: (-x.get('length of service', 0), x.get('name', '')))

    # Format the data
    formatted_data = []
    for employee in sorted_data:
        formatted_data.append(f"{employee.get('name', 'Unknown')} is {employee.get('age', 'Unknown')} years old, works in the {employee.get('department', 'Unknown')} department as a {employee.get('job role', 'Unknown')}, and has been with the firm for {employee.get('length of service', 'Unknown')} years.")

    return formatted_data