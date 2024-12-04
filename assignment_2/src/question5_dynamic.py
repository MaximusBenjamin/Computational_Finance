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

def analyze_cascade_with_enhanced_bailout(G, failing_bank, bailout_fund_limit):
    """
    Analyze cascading failures with a more robust bailout strategy focused on critical banks.
    """
    bailout_fund = bailout_fund_limit
    affected_banks = set()
    processing_queue = [failing_bank]
    critical_banks = set()
    
    # Trigger the failure of the initial bank
    G.nodes[failing_bank]['equity'] = 0  # Failing bank equity set to zero
    
    while processing_queue:
        current_bank = processing_queue.pop(0)
        
        for neighbor in G.successors(current_bank):
            exposure = G[current_bank][neighbor]['exposure']
            
            # Calculate the equity of the neighbor after absorbing the exposure
            reduced_equity = G.nodes[neighbor]['equity'] - exposure
            
            # Use the bailout fund to prevent the neighbor from failing
            if reduced_equity < 0 and bailout_fund > 0:
                needed_bailout = -reduced_equity  # Amount needed to stabilize
                bailout_applied = min(needed_bailout, bailout_fund)
                bailout_fund -= bailout_applied
                reduced_equity += bailout_applied  # Adjust equity after bailout
            
            # Update the neighbor's equity
            G.nodes[neighbor]['equity'] = reduced_equity
            
            # If the neighbor fails, add it to the cascade
            if reduced_equity < 0 and neighbor not in affected_banks:
                affected_banks.add(neighbor)
                processing_queue.append(neighbor)
                critical_banks.add(neighbor)

    # Capture final equity states
    equity_states = {node: data['equity'] for node, data in G.nodes(data=True)}
    return affected_banks, equity_states, bailout_fund, critical_banks

# Simulate for all banks and output results
bailout_fund_limit = 10.0  # in billion euros
bailout_results = {}

for bank in equity_sheet['Bank']:
    G_temp = create_network(equity_sheet, exposure_sheet)
    affected_banks, final_equities, remaining_bailout_fund, critical_banks = analyze_cascade_with_enhanced_bailout(
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
