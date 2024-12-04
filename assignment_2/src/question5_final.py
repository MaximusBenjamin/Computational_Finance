import pandas as pd
import networkx as nx

# Load the Excel file
file_path = 'banks_v2.xlsx'
equity_sheet = pd.read_excel(file_path, sheet_name='equity')
exposure_sheet = pd.read_excel(file_path, sheet_name='counterparty_exposures')

def create_network(equity_sheet, exposure_sheet):
    """
    Create a directed graph representing the banking network.
    """
    G = nx.DiGraph()
    for _, row in equity_sheet.iterrows():
        G.add_node(row['Bank'], name=row['Name'], equity=row['Equity'])
    for _, row in exposure_sheet.iterrows():
        G.add_edge(row['Bank1'], row['Bank2'], exposure=row['exposure'])
    return G

def analyze_cascade_with_optimal_bailout(G, failing_bank, bailout_fund_limit):
    """
    Optimized bailout logic: dynamically prioritize banks with systemic importance and apply funds proactively.
    """
    bailout_fund = bailout_fund_limit
    affected_banks = set()
    processing_queue = [failing_bank]
    critical_banks = set()
    
    # Trigger the failure of the initial bank
    G.nodes[failing_bank]['equity'] = 0  # Failing bank equity set to zero

    while processing_queue:
        # Re-evaluate priorities at each step
        current_failures = {}
        # Track the potential impact of each bank failure
        for current_bank in processing_queue:
            for neighbor in G.successors(current_bank):
                exposure = G[current_bank][neighbor]['exposure']
                reduced_equity = G.nodes[neighbor]['equity'] - exposure
                
                # Calculate cascade impact (banks that would fail if this bank fails)
                cascade_impact = sum(
                    1 for n in G.successors(neighbor) 
                    if G.nodes[n]['equity'] - G[neighbor][n]['exposure'] < 0
                )
                current_failures[neighbor] = (reduced_equity, cascade_impact)
        
        # Sort by two criteria: 
        # 1. Cascade impact (high priority for the largest impact)
        # 2. Reduced equity (prefer saving banks that are closer to failure)
        sorted_failures = sorted(
            current_failures.items(),
            key=lambda x: (-x[1][1], x[1][0])  # prioritize cascade impact, then equity
        )
        
        # Process failures in prioritized order
        new_queue = []
        for bank, (reduced_equity, _) in sorted_failures:
            if reduced_equity < 0 and bailout_fund > 0:
                # Apply bailout fund dynamically to stop cascade
                needed_bailout = -reduced_equity  # Amount needed to stabilize
                bailout_applied = min(needed_bailout, bailout_fund)
                bailout_fund -= bailout_applied
                reduced_equity += bailout_applied
            
            # Update the equity state after bailout
            G.nodes[bank]['equity'] = reduced_equity
            
            # If the bank fails, add it to the cascade
            if reduced_equity < 0 and bank not in affected_banks:
                affected_banks.add(bank)
                new_queue.append(bank)
                critical_banks.add(bank)
        
        # Update the processing queue for the next iteration
        processing_queue = new_queue

    # Capture final equity states after all bailout decisions
    equity_states = {node: data['equity'] for node, data in G.nodes(data=True)}
    return affected_banks, equity_states, bailout_fund, critical_banks

# Simulate the optimized bailout logic for every bank
bailout_fund_limit = 10.0  # 10 billion euros
bailout_results = {}

# Simulate for all banks
for bank in equity_sheet['Bank']:
    G_temp = create_network(equity_sheet, exposure_sheet)
    affected_banks, final_equities, remaining_bailout_fund, critical_banks = analyze_cascade_with_optimal_bailout(
        G_temp, bank, bailout_fund_limit
    )
    bailout_results[bank] = {
        'affected_banks': affected_banks,
        'final_equities': final_equities,
        'remaining_bailout_fund': remaining_bailout_fund,
        'critical_banks': critical_banks
    }

# Print detailed results
print("\nBailout Results for Each Bank:")
for bank, result in bailout_results.items():
    print(f"\nBank {bank}:")
    print(f"  Affected Banks: {', '.join(map(str, result['affected_banks'])) or 'None'}")
    print(f"  Remaining Bailout Fund: {result['remaining_bailout_fund']:.2f} billion")
    print("  Final Equity States:")
    for b, equity in result['final_equities'].items():
        print(f"    Bank {b}: {equity:.2f} billion")

# Print summary
print("\nSummary:")
print(f"{'Failing Bank':<15} {'Affected Banks':<20} {'Remaining Bailout Fund (billion)':<30}")
for bank, result in bailout_results.items():
    num_affected = len(result['affected_banks'])
    remaining_fund = result['remaining_bailout_fund']
    print(f"{bank:<15} {num_affected:<20} {remaining_fund:<30.2f}")