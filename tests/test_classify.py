from netml.pparser.parser import PCAP
from netml.utils.tool import load_data

pcap = PCAP(
    'examples/data/demo.pcap',
    flow_ptks_thres=2,
    random_state=42,
    verbose=10,
)

# extract flows from pcap
pcap.pcap2flows(q_interval=0.9)

# extract features from each flow given feat_type
pcap.flow2features('IAT', fft=False, header=False)

(model, train_history) = load_data('models/OCSVM-results2.dat')

model.predict(pcap.features)