from gurobipy import Model, GRB

# Create a new Gurobi model
model = Model("Production_Synchronization")

# Parameters
actimel_cycle = 28  # Actimel production cycle in hours
danonino_cycle = 5 * 24  # Danonino production cycle in hours (5 days)
total_hours_in_week = 7 * 24  # Total hours in a week (168 hours)
offset_time = danonino_cycle - actimel_cycle  # Danonino needs to start this many hours before Actimel

# Decision Variables

# Start time for Actimel production (in hours, from the start of the week)
start_ermi = model.addVar(name="start_ermi", vtype=GRB.INTEGER, lb=0, ub=total_hours_in_week-1)

# Start time for Danonino production
start_arcil = model.addVar(name="start_arcil", vtype=GRB.INTEGER, lb=0, ub=total_hours_in_week-1)

# Additional variable to handle the week shift (if start_ermi - offset_time goes out of range)
week_shift = model.addVar(name="week_shift", vtype=GRB.INTEGER, lb=-1, ub=1)

# Auxiliary variable to represent the day of the week for Danonino production start
start_day_arcil = model.addVar(name="start_day_arcil", vtype=GRB.INTEGER, lb=0, ub=6)

# Constraints
# Ensure Danonino starts exactly `offset_time` hours before Actimel, considering cyclic nature of weeks
model.addConstr(start_arcil == start_ermi - offset_time - week_shift * total_hours_in_week, name="synchronization")

# Bound start_arcil to its corresponding day (from start_day_arcil)
model.addConstr(start_arcil >= start_day_arcil * 24, name="arcil_day_lower_bound")  # Lower bound
model.addConstr(start_arcil <= (start_day_arcil + 1) * 24 - 1, name="arcil_day_upper_bound")  # Upper bound

# Constraint 2: Arcil (Danonino production) can only operate between Monday 00:00 and Friday 23:59
model.addConstr(start_day_arcil >= 0, name="arcil_weekday_lower_bound")  # Cannot start before Monday
model.addConstr(start_day_arcil <= 4, name="arcil_weekday_upper_bound")  # Cannot start after Friday

# Objective: Minimize the start time for Actimel production
model.setObjective(start_ermi, GRB.MINIMIZE)

# Optimize the model
model.optimize()

# Display the results
if model.status == GRB.OPTIMAL:
    # Get the start times for Ermi and Arcil
    start_time_ermi = start_ermi.X
    start_time_arcil = start_arcil.X
    
    # Display results in terms of day and hour
    def convert_to_day_hour(time_in_hours):
        days = int(time_in_hours // 24)  # Calculate number of days
        hours = int(time_in_hours % 24)  # Calculate remaining hours
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return f"{days_of_week[days]} at {hours}:00"

    # Output schedule
    print(f"Optimal start time for Ermi (Actimel): {convert_to_day_hour(start_time_ermi)}")
    print(f"Optimal start time for Arcil (Danonino): {convert_to_day_hour(start_time_arcil)}")
else:
    print("No optimal solution found.")



