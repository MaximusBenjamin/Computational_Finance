import pandas as pd
import networkx as nx

#  Importing excel file, contains two sheets, one with the exposures and the other with total equity used to analyze bank failures
file_path = 'banks_v2.xlsx'
equity_sheet = pd.read_excel(file_path, sheet_name='equity')
exposure_sheet = pd.read_excel(file_path, sheet_name='counterparty_exposures')

def create_network(equity_sheet, exposure_sheet):
    # Directed graph to observe the network of banks 
    G = nx.DiGraph()
    for _, row in equity_sheet.iterrows():
        G.add_node(row['Bank'], name=row['Name'], equity=row['Equity'])
    for _, row in exposure_sheet.iterrows():
        G.add_edge(row['Bank1'], row['Bank2'], exposure=row['exposure'])
    return G

def analyze_cascade_with_optimal_bailout(G, failing_bank, bailout_fund_limit):
    # Dynamically optimize bailout distribution by analyzing the impact of each bank based on the interconnectedness and proactively assess the potential failures.
    bailout_fund = bailout_fund_limit
    affected_banks = set()
    processing_queue = [failing_bank]
    critical_banks = set()
    
    # Trigger the failure of the initial bank
    G.nodes[failing_bank]['equity'] = 0  # This ensures that if a bank is considered 'failed' their equity is set to 0.

    while processing_queue:
        current_failures = {}
        # Tracking the potential impact, and storign it in a list to ensure we keep track of it
        for current_bank in processing_queue:
            for neighbor in G.successors(current_bank):
                exposure = G[current_bank][neighbor]['exposure']
                reduced_equity = G.nodes[neighbor]['equity'] - exposure
                
                # Calculating the cascade impact, meaning that banks that would fail as a result of bank x failing
                cascade_impact = sum(
                    1 for n in G.successors(neighbor) 
                    if G.nodes[n]['equity'] - G[neighbor][n]['exposure'] < 0
                )
                current_failures[neighbor] = (reduced_equity, cascade_impact)
        
        # Sorting: We need to ensure that we find the most cost effective path to preventing cascade failures
        # This is done to minimize the total bailout fund we need to prevent cascading, here's how we sorted it:
        # 1.  Cascade impact (HIgh priority for the alrgest impact)
        # 2.  The lowest equity (Prefer saving banks that are closer to failure)
        sorted_failures = sorted(
            current_failures.items(),
            key=lambda x: (-x[1][1], x[1][0])  # prioritize cascade impact, then equity
        )
        
        new_queue = []
        for bank, (reduced_equity, _) in sorted_failures:
            if reduced_equity < 0 and bailout_fund > 0:
                # Here we apply the fund dynamically based on the priorities. This results in a significant reduction in cascading vs just applying the fund at random/sequentially.
                needed_bailout = -reduced_equity  # Amount needed for stabilit
                bailout_applied = min(needed_bailout, bailout_fund)
                bailout_fund -= bailout_applied
                reduced_equity += bailout_applied
            
            # Assign the new equity state value 
            G.nodes[bank]['equity'] = reduced_equity
            
            # If the bank fails here we simply append it to keep track of the failed banks
            if reduced_equity < 0 and bank not in affected_banks:
                affected_banks.add(bank)
                new_queue.append(bank)
                critical_banks.add(bank)
        
        # Here we update the queue to prepare for the next iterations
        processing_queue = new_queue

    # After our bailout, we create a list here with the final equity states
    equity_states = {node: data['equity'] for node, data in G.nodes(data=True)}
    return affected_banks, equity_states, bailout_fund, critical_banks

# Monte carlo simulation with the given parameters in the question 
bailout_fund_limit = 10.0  # 10 billion euros
bailout_results = {}

# Simulate for every single bank 
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

# Printing the results per bank, more as a debug 
print("\nBailout Results for Each Bank:")
for bank, result in bailout_results.items():
    print(f"\nBank {bank}:")
    print(f"  Affected Banks: {', '.join(map(str, result['affected_banks'])) or 'None'}")
    print(f"  Remaining Bailout Fund: {result['remaining_bailout_fund']:.2f} billion")
    print("  Final Equity States:")
    for b, equity in result['final_equities'].items():
        print(f"    Bank {b}: {equity:.2f} billion")

# Print summary, the 'affected_banks' here refers to the amount of banks affected and not a specific bank. 
print("\nSummary:")
print(f"{'Failing Bank':<15} {'Affected Banks':<20} {'Remaining Bailout Fund (billion)':<30}")
for bank, result in bailout_results.items():
    num_affected = len(result['affected_banks'])
    remaining_fund = result['remaining_bailout_fund']
    print(f"{bank:<15} {num_affected:<20} {remaining_fund:<30.2f}")
