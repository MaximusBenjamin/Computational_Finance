import pandas as pd
import networkx as nx

# Load the Excel file
file_path = 'banks_v2.xlsx'
equity_sheet = pd.read_excel(file_path, sheet_name='equity')
exposure_sheet = pd.read_excel(file_path, sheet_name='counterparty_exposures')

def create_network(equity_sheet, exposure_sheet):
    # Directed graph representing the total network of banksk etc

    G = nx.DiGraph()
    for _, row in equity_sheet.iterrows():
        G.add_node(row['Bank'], name=row['Name'], equity=row['Equity'])
    for _, row in exposure_sheet.iterrows():
        G.add_edge(row['Bank1'], row['Bank2'], exposure=row['exposure'])
    return G

def analyze_cascade_with_dynamic_bailout(G, failing_bank, bailout_fund_limit):
    """
    Optimized bailout logic: dynamically prioritize banks with systemic importance and apply funds proactively.
    """
    bailout_fund = bailout_fund_limit
    affected_banks = set()
    processing_queue = [failing_bank]
    critical_banks = set()
    
    # Trigger the initial failure, we do this by just setting equity to 0
    G.nodes[failing_bank]['equity'] = 0  # Failing bank equity set to zero

    while processing_queue:
        current_failures = {}
        # Here we store the potential impacts of the failures into a list to keep track of
        for current_bank in processing_queue:
            for neighbor in G.successors(current_bank):
                exposure = G[current_bank][neighbor]['exposure']
                reduced_equity = G.nodes[neighbor]['equity'] - exposure
                
                # Here we calculate the failed banks based on the equity sheet and exposure sheet, this includes the indirect and direct effect
                cascade_impact = sum(
                    1 for n in G.successors(neighbor) 
                    if G.nodes[n]['equity'] - G[neighbor][n]['exposure'] < 0
                )
                current_failures[neighbor] = (reduced_equity, cascade_impact)
        
        # Now in order to effectively apply the bailout fund we need to find the most optimal pathway to prevent cascade failing, so we sorted it based on these two criterias
        # 1. Cascade impact (highest cascade impact)
        # 2. reduced equity (saving the banks that are closest to failure)
        sorted_failures = sorted(
            current_failures.items(),
            key=lambda x: (-x[1][1], x[1][0])  # prioritize cascade impact, then equity
        )
        
        new_queue = []
        for bank, (reduced_equity, _) in sorted_failures:
            if reduced_equity < 0 and bailout_fund > 0:
                needed_bailout = -reduced_equity
                bailout_applied = min(needed_bailout, bailout_fund)
                bailout_fund -= bailout_applied
                reduced_equity += bailout_applied
            
            G.nodes[bank]['equity'] = reduced_equity
            
            if reduced_equity < 0 and bank not in affected_banks:
                affected_banks.add(bank)
                new_queue.append(bank)
                critical_banks.add(bank)
        
        processing_queue = new_queue

    equity_states = {node: data['equity'] for node, data in G.nodes(data=True)}
    return affected_banks, equity_states, bailout_fund, critical_banks

def find_most_cost_effective_bailout(G, failing_bank, bailout_fund_limit):

    # Here we further add to robustness and determine the most cost effective distribution 

    bailout_fund = bailout_fund_limit
    bailout_plan = []
    
    affected_banks, equity_states, remaining_fund, _ = analyze_cascade_with_dynamic_bailout(G, failing_bank, bailout_fund)
    if not affected_banks:
        return bailout_plan, remaining_fund, equity_states  # No bail needed (bank survives)

    while bailout_fund > 0 and affected_banks:
        # Here we analyze the bank impact, basically the highest effect on the cascade 
        impacts = {}
        for bank in affected_banks:
            temp_G = G.copy()
            temp_G.nodes[bank]['equity'] += bailout_fund  # Create a temporary node which temporarily saves the bank
            _, _, temp_remaining_fund, temp_critical_banks = analyze_cascade_with_dynamic_bailout(temp_G, failing_bank, bailout_fund)
            impacts[bank] = len(affected_banks) - len(temp_critical_banks)  # Improvement in cascade
        
        # Here we sort through and find the bank which has the maximize saved effect per unit of bailout fund spent
        best_bank = max(impacts, key=impacts.get)
        bailout_needed = -G.nodes[best_bank]['equity'] if G.nodes[best_bank]['equity'] < 0 else 0
        bailout_used = min(bailout_needed, bailout_fund)
        
        if bailout_used > 0:
            bailout_fund -= bailout_used
            G.nodes[best_bank]['equity'] += bailout_used
            bailout_plan.append((best_bank, bailout_used))
        
        # Re-analyze with the newly stored states
        affected_banks, equity_states, remaining_fund, _ = analyze_cascade_with_dynamic_bailout(G, failing_bank, bailout_fund)

    return bailout_plan, bailout_fund, equity_states

def find_minimum_bailout_fund_to_prevent_cascade(equity_sheet, exposure_sheet, step=0.1, max_fund=100000.0):
    """
    Find the minimum bailout fund size that prevents any cascade from happening.  
    """
    fund_size = step
    while fund_size <= max_fund:
        no_cascade = True
        for bank in equity_sheet['Bank']:
            G_temp = create_network(equity_sheet, exposure_sheet)
            affected_banks, _, _, _ = analyze_cascade_with_dynamic_bailout(G_temp, bank, fund_size)
            if len(affected_banks) > 0:  # Here cascade occurs, so we go back and increase the fund size as it isn't sufficient
                no_cascade = False
                break
        if no_cascade:  # This is the case if no cascade is found, and thus we have minimized the cascading effect with the least fund size
            return fund_size
        fund_size += step
    return None  # This is in case the parameters aren't large enough so we might need to increase the simulation size sinze right now the max is set to 100k

# Finding the minimum fund required, we use a step of 1.0, but you could go lower but it will take longer to run, so maybe 0.1 next
G = create_network(equity_sheet, exposure_sheet)
minimum_fund_needed = find_minimum_bailout_fund_to_prevent_cascade(equity_sheet, exposure_sheet, step=1.0, max_fund=100000.0)

# Here we simply print and also output the most cost-effective plan to bailout 
failing_bank = equity_sheet['Bank'][0]  # Here we choose the first bank
if minimum_fund_needed is not None:
    bailout_plan, remaining_fund, equity_states = find_most_cost_effective_bailout(G, failing_bank, minimum_fund_needed)
    print(f"\nMinimum bailout fund required to prevent any cascade: {minimum_fund_needed:.2f}")
    print("Cost-effective bailout plan:")
    for bank, amount in bailout_plan:
        print(f"  - Bank {bank}: {amount:.2f}")
    print(f"Remaining fund after bailout: {remaining_fund:.2f}")
else:
    print("\nNo bailout fund within the tested range was sufficient to prevent cascading failures.")
