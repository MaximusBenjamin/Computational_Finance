import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Importing the data set
data = pd.ExcelFile('returns.xlsx')
returns_data = data.parse('histreturns')
proc_data = returns_data.iloc[1:, :4] # proc = processed data
proc_data.columns = ["Year", "US_TBonds", "Corp_Bonds", "SP500_Total_Return"]
proc_data["Year"] = proc_data["Year"].astype(int)
proc_data["US_TBonds"] = pd.to_numeric(proc_data["US_TBonds"], errors='coerce')
proc_data["Corp_Bonds"] = pd.to_numeric(proc_data["Corp_Bonds"], errors='coerce')
proc_data["SP500_Total_Return"] = pd.to_numeric(proc_data["SP500_Total_Return"], errors='coerce')

# Simulation input values 
initial_portfolio = 1000000  # Initial portfolio value 
swr = 0.035  # Safe withdrawl rate, we assume 3.5% in the question later
wealth_tax = 0.0  # Annual wealth tax, set to 0 currently, but in Q1 was different
retirement_years = 40  # Retirement period in years
asset_allocation = {"stocks": 0.8, "bonds": 0.18, "cash": 0.02}  # Portfolio weights, basically how much the participant invests in each asset class 
y_contribution = 0 # the yearly contribution made by participant

# List to store the values from the simulation

simulation_results = []


# Looping through the year range specified in the question, although I added 1 more year because we have sufficient data.
for start_year in range(1928, 1981):
    portfolio_trajectories = []  # Store the value for each year
    portfolio_balance = initial_portfolio
    failed = False
    
    # Extrating the data 
    historical_returns = proc_data[(proc_data["Year"] >= start_year) & 
                                       (proc_data["Year"] < start_year + retirement_years)]
    
    # Since we only have data from 1928 - 2022, the latest we can start retirement is 1982 otherwise no data points left
    if len(historical_returns) < retirement_years:
        continue

    portfolio_balance = initial_portfolio + y_contribution  # Initial investment includes $1,000,000 + $25,000
    portfolio_trajectories = [portfolio_balance]  # Record the initial investment as the first point in the trajectory

    # Running the actual simulation for each year 
    for i in range(retirement_years):
        # Annual withdrawal (How much participant withdraws each year)
        annual_withdrawal = portfolio_balance * swr
        portfolio_balance -= annual_withdrawal

        # Apply wealth tax
        portfolio_balance -= portfolio_balance * wealth_tax

        # Calculate total returns for the year
        year_data = historical_returns.iloc[i]
        annual_return = (
            year_data["SP500_Total_Return"] * asset_allocation["stocks"] +
            year_data["Corp_Bonds"] * asset_allocation["bonds"] +
            year_data["US_TBonds"] * asset_allocation["cash"]
        )
        portfolio_balance += portfolio_balance * annual_return

        # Add the yearly contribution (left here in case we still add, but I think in this question we don't add the yearly contribution since its focused on withdrawl)
        portfolio_balance += y_contribution

        # Record the portfolio balance for the year
        portfolio_trajectories.append(portfolio_balance)

        # Check for portfolio failure
        if portfolio_balance <= 0:
            failed = True
            break


    simulation_results.append({
        "start_year": start_year,
        "portfolio_trajectories": portfolio_trajectories,
        "failed": failed
    })


plt.figure(figsize=(12, 6))
for result in simulation_results:
    trajectory = result["portfolio_trajectories"]
    if result["failed"]:
        # Plot portfolio balance in millions (Because otherwise its e^06 etc)
        plt.plot(range(len(trajectory)), [x / 1_000_000 for x in trajectory], color="red", alpha=0.5)
    else:
        plt.plot(range(len(trajectory)), [x / 1_000_000 for x in trajectory], color="gray", alpha=0.5)

plt.title("Retirement Portfolio Trajectories (1928-1980 Start Years)")
plt.xlabel("Retirement Years")
plt.ylabel("Portfolio Balance (€ millions)")  # Update y-axis label
plt.axhline(0, color="black", linestyle="--", linewidth=1, alpha=0.8)
plt.grid()

# Format the y-axis to show millions (Because otherwise its e^06 etc)
plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}M'))

plt.show()

# Highliting the failed ones
plt.title("Retirement Portfolio Trajectories (1928-1980 Start Years)")
plt.xlabel("Retirement Years")
plt.ylabel("Portfolio Balance (€)")
plt.axhline(0, color="black", linestyle="--", linewidth=1, alpha=0.8)
plt.grid()   
plt.show()

total_failures = sum(1 for result in simulation_results if result["failed"])
total_simulations = len(simulation_results)
print(f"Failures: {total_failures}/{total_simulations} simulations")
print(f"Success Rate: {100 - (total_failures / total_simulations) * 100:.2f}%")



