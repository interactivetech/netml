from netml.pparser.parser import PCAP
from netml.utils.tool import dump_data, load_data

pcap = PCAP('examples/data/demo.pcap', flow_ptks_thres=2)

pcap.pcap2flows()

# Extract inter-arrival time features
pcap.flow2features('IAT', fft=False, header=False)

iat_features = pcap.features