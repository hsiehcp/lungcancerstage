import re
import streamlit as st

# Load the file
file_path = 'lungcastage.mkd'
with open(file_path, 'r') as file:
    file_content = file.read()

# Parse the TNM Classification and Stages from the document
tnm_classification = {'T': {}, 'N': {}, 'M': {}}
current_section = None

lines = file_content.split('\n')
for line in lines:
    if line.startswith('####'):
        section = line.split()[-1].strip('()')
        if section in tnm_classification:
            current_section = section
    elif current_section and line.startswith('- **'):
        code_match = re.search(r'\*\*(.*?)\*\*', line)
        if code_match:
            code = code_match.group(1)
            description = line.split(':', 1)[1].strip() if ':' in line else ''
            tnm_classification[current_section][code] = description

# Define the staging system
stages = {
    'Stage 0': ['Tis N0 M0'],
    'Stage IA1': ['T1a(mi) N0 M0'],
    'Stage IA2': ['T1a N0 M0'],
    'Stage IA3': ['T1b N0 M0'],
    'Stage IB': ['T1c N0 M0', 'T2a N0 M0'],
    'Stage IIA': ['T2b N0 M0'],
    'Stage IIB': ['T1a N1 M0', 'T1b N1 M0', 'T1c N1 M0', 'T2a N1 M0', 'T2b N1 M0', 'T3 N0 M0'],
    'Stage IIIA': ['T1a N2 M0', 'T1b N2 M0', 'T1c N2 M0', 'T2a N2 M0', 'T2b N2 M0', 'T3 N1 M0', 'T4 N0 M0', 'T4 N1 M0'],
    'Stage IIIB': ['T1a N3 M0', 'T1b N3 M0', 'T1c N3 M0', 'T2a N3 M0', 'T2b N3 M0', 'T3 N2 M0', 'T4 N2 M0'],
    'Stage IIIC': ['T3 N3 M0', 'T4 N3 M0'],
    'Stage IVA': ['Any T Any N M1a', 'Any T Any N M1b'],
    'Stage IVB': ['Any T Any N M1c'],
}

# Extend staging definitions to handle ranges
def extend_stages(stages):
    extended_stages = {}
    for stage, tnm_list in stages.items():
        extended_list = []
        for tnm in tnm_list:
            parts = tnm.split()
            t_part = parts[0]
            n_part = parts[1]
            m_part = parts[2]

            t_values = expand_range(t_part)
            n_values = expand_range(n_part)
            m_values = expand_range(m_part)

            for t in t_values:
                for n in n_values:
                    for m in m_values:
                        extended_list.append(f"{t} {n} {m}")
        extended_stages[stage] = extended_list
    return extended_stages

def expand_range(part):
    if '-' in part:
        base = part[0]
        start = int(part[1])
        end = int(part[3])
        return [f"{base}{i}" for i in range(start, end + 1)]
    elif 'Any' in part:
        return ['Any']
    else:
        return [part]

extended_stages = extend_stages(stages)

# Function to determine the stage
def determine_stage(t, n, m):
    tnm = f'{t} {n} {m}'
    for stage, combinations in extended_stages.items():
        if tnm in combinations:
            return stage
        if f'Any {n} {m}' in combinations:
            return stage
        if f'{t} Any {m}' in combinations:
            return stage
        if f'Any Any {m}' in combinations:
            return stage
    if m == 'M1a' or m == 'M1b':
        return 'Stage IVA'
    if m == 'M1c':
        return 'Stage IVB'
    return 'Stage not found'

# Streamlit app
st.title("Lung Cancer Staging")

# Display the entire content of lungcastage.mkd as formatted markdown
st.write("### Full Content of lungcastage.mkd:\n")
st.markdown(file_content)

# Create pulldown menus for T, N, and M values
t_values = ['TX', 'T0', 'T1a(mi)', 'T1a', 'T1b', 'T1c', 'T2a', 'T2b', 'T3', 'T4']
n_values = ['NX', 'N0', 'N1', 'N2', 'N3']
m_values = ['M0', 'M1a', 'M1b', 'M1c']

t = st.selectbox("Select the Tumor (T) value:", t_values)
n = st.selectbox("Select the Node (N) value:", n_values)
m = st.selectbox("Select the Metastasis (M) value:", m_values)

if st.button("Submit"):
    # Determine and display the stage
    stage = determine_stage(t, n, m)
    st.write(f"\n### The stage for T={t}, N={n}, M={m} is: {stage}")

