# netml learn --pcap-abnormal=examples/data/srcIP_10.42.0.1/srcIP_10.42.0.119_anomaly.pcap \
#                 --output=models/model.dat 
netml learn --pcap=examples/data/demo.pcap           \
            --label=examples/data/demo.csv           \
            --output=models/OCSVM-results.dat