from netml.pparser.parser import PCAP

# pcap = PCAP('examples/data/demo.pcap')
pcap = PCAP('examples/data/srcIP_10.42.0.1/srcIP_10.42.0.1_normal.pcap')

pcap.pcap2pandas()

pdf = pcap.df
print(pdf.columns)