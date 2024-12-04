import pandas as pd
import networkx as nx

# Import the file provided by lecturer

file_path = 'banks_v2.xlsx'
equity_sheet = pd.read_excel(file_path, sheet_name='equity')
exposure_sheet = pd.read_excel(file_path, sheet_name='counterparty_exposures')


# Create network based on the excel file, equity sheet containing the total equity and exposure is used for the network and interconnectedness
def create_network(equity_sheet, exposure_sheet):
    G = nx.DiGraph()
    for _, row in equity_sheet.iterrows():
        G.add_node(row['Bank'], name=row['Name'], equity=row['Equity'])
    for _, row in exposure_sheet.iterrows():
        G.add_edge(row['Bank1'], row['Bank2'], exposure=row['exposure'])
    return G

# Here we anaylze the cascade effect of each bank, basically we check whether the equity - exposure  (to failed bank) is less than 0, which would indicate that a bank went bankrupt, we analyze the indirect effect here too.
def analyze_cascade(G, failing_bank):
    affected_banks = set()
    processing_queue = [failing_bank]
    while processing_queue:
        current_bank = processing_queue.pop(0)
        for neighbor in G.successors(current_bank):
            exposure = G[current_bank][neighbor]['exposure']
            G.nodes[neighbor]['equity'] -= exposure
            if G.nodes[neighbor]['equity'] < 0 and neighbor not in affected_banks:
                affected_banks.add(neighbor) 
                processing_queue.append(neighbor)
    equity_states = {node: data['equity'] for node, data in G.nodes(data=True)} # New equity states
    return affected_banks, equity_states 

cascade_results = {} # Created a list to store all the cascade results
for bank in equity_sheet['Bank']:
    if bank != 1:
        G_temp = create_network(equity_sheet, exposure_sheet)
        affected_banks, _ = analyze_cascade(G_temp, bank)
        cascade_results[bank] = affected_banks

# Print the results for each bank. 
print("Cascade results for each bank:")
for bank, affected in cascade_results.items():
    print(f"Failure of Bank {bank} affects: {', '.join(map(str, affected)) or 'No other banks'}")
