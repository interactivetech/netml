from netml.pparser.parser import PCAP
from netml.utils.tool import dump_data

pcap = PCAP(
    'examples/data/demo.pcap',
    flow_ptks_thres=2,
    random_state=42,
    verbose=10,
)

# extract flows from pcap
pcap.pcap2flows(q_interval=0.9)

# label each flow (optional)
pcap.label_flows(label_file='examples/data/demo.csv')

# extract features from each flow via IAT
pcap.flow2features('IAT', fft=False, header=False)

# dump data to disk
dump_data((pcap.features, pcap.labels), out_file='models/IAT-features.dat')

# stats
print(pcap.features.shape, pcap.pcap2flows.tot_time, pcap.flow2features.tot_time)