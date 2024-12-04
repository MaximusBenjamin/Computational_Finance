import pandas as pd
import networkx as nx

# Load the Excel file
file_path = 'banks_v2.xlsx'
equity_sheet = pd.read_excel(file_path, sheet_name='equity')
exposure_sheet = pd.read_excel(file_path, sheet_name='counterparty_exposures')

def create_network(equity_sheet, exposure_sheet):
    G = nx.DiGraph()
    for _, row in equity_sheet.iterrows():
        G.add_node(row['Bank'], name=row['Name'], equity=row['Equity'])
    for _, row in exposure_sheet.iterrows():
        G.add_edge(row['Bank1'], row['Bank2'], exposure=row['exposure'])
    return G

def analyze_jpm_failure(G):
    jpm_node = 1  # JPM is Bank 1
    # Set JPM's equity to 0 to simulate failure
    G.nodes[jpm_node]['equity'] = 0
    # Adjust the equity of other banks
    for neighbor in G.successors(jpm_node):
        exposure = G[jpm_node][neighbor]['exposure']
        G.nodes[neighbor]['equity'] -= exposure
    # Return equity states
    equity_states = {node: data['equity'] for node, data in G.nodes(data=True)}
    return equity_states

G = create_network(equity_sheet, exposure_sheet)
jpm_failure_result = analyze_jpm_failure(G)

# Print results
print("Equity states after JPM failure:")
for bank, equity in jpm_failure_result.items():
    print(f"Bank {bank}: {equity:.2f} billion")
