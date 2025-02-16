# netml

`netml` is a network anomaly detection tool & library written in Python.

The library contains two primary submodules:

* `pparser`: pcap parser\
Parse pcaps to produce flow features using [Scapy](https://scapy.net/).\
(Additional functionality to map pcaps to pandas DataFrames.)

* `ndm`: novelty detection modeling\
Detect novelties / anomalies, via different models, such as OCSVM.

The tool's command-line interface is documented by its built-in help flags such as `-h` and `--help`:

    netml --help


## Installation

The `netml` library is available on [PyPI](https://pypi.org/project/netml/):

    pip install netml

Or, from a repository clone:

    pip install .

### CLI

The CLI tool is available as a distribution "extra":

    pip install netml[cli]

Or:

    pip install .[cli]

#### Tab-completion

Shell tab-completion is provided by [`argcomplete`](https://github.com/kislyuk/argcomplete) (through `argcmdr`). Completion code appropriate to your shell may be generated by `register-python-argcomplete`, _e.g._:

    register-python-argcomplete --shell=bash netml

The results of the above should be evaluated, _e.g._:

    eval "$(register-python-argcomplete --shell=bash netml)"

Or, to ensure the above is evaluated for every session, _e.g._:

    register-python-argcomplete --shell=bash netml > ~/.bash_completion

For more information, refer to `argcmdr`: [Shell completion](https://github.com/dssg/argcmdr/tree/0.6.0#shell-completion).


## Use

### Simple data manipulation

#### Packet captures to pandas DataFrames

```python
from netml.pparser.parser import PCAP

pcap = PCAP('data/demo.pcap')

pcap.pcap2pandas()

pdf = pcap.df
```

#### Packet captures to flow-based features

```python
from netml.pparser.parser import PCAP
from netml.utils.tool import dump_data, load_data

pcap = PCAP('data/demo.pcap', flow_ptks_thres=2)

pcap.pcap2flows()

# Extract inter-arrival time features
pcap.flow2features('IAT', fft=False, header=False)

iat_features = pcap.features
```

Possible features to pass to `flows2features` include:

* `IAT`: A flow is represented as a timeseries of inter-arrival times between
  packets, *i.e.*, elapsed time in seconds between any two packets in the flow.

* `STATS`: A flow is represented as a set of statistical quantities. We choose
  12 of the most common such statistics in the literature: flow duration, number of
  packets sent per second, number of bytes per second, and various statistics on
  packet sizes within each flow: mean, standard deviation, inter-quartile range,
  minimum, and maximum. Finally, the total number of packets and total number
  of bytes for each flow.

* `SIZE`: A flow is represented as a timeseries of packet sizes in bytes, with one
  sample per packet.

* `SAMP-NUM`: A flow is partitioned into small intervals of equal length 𝛿𝑡, and
  the number of packets in each interval is recorded; thus, a flow is
  represented as a timeseries of packet counts in small time intervals, with one
  sample per time interval. Here, 𝛿𝑡 might be viewed as a choice of sampling
  rate for the timeseries, hence the nomenclature.

* `SAMP-SIZE`: A flow is partitioned into time intervals of equal length 𝛿𝑡, and
  the total packet size (*i.e.*, byte count) in each interval is recorded; thus, a
  flow is represented as a timeseries of byte counts in small time intervals,
  with one sample per time interval.

### Classification of network traffic for outlier detection

Having [trained a model](#training-a-network-traffic-model) to your network traffic,
the identification of anomalous traffic is as simple as providing a packet capture (PCAP)
file to the `netml classify` command of the CLI:

    netml classify --model=model.dat < unclassified.pcap

Using the Python library, the same might be accomplished, _e.g._:

```python
from netml.pparser.parser import PCAP
from netml.utils.tool import load_data

pcap = PCAP(
    'unclassified.pcap',
    flow_ptks_thres=2,
    random_state=42,
    verbose=10,
)

# extract flows from pcap
pcap.pcap2flows(q_interval=0.9)

# extract features from each flow given feat_type
pcap.flow2features('IAT', fft=False, header=False)

(model, train_history) = load_data('model.dat')

model.predict(pcap.features)
```

### Training a network traffic model

A model may be trained for outlier detection as simply as providing a PCAP file to the `netml learn` command:

    netml learn --pcap=traffic.pcap \
                --output=model.dat

(Note that for clarity and consistency with the `classify` command, the flags `--output` and `--model` are synonymous to the `learn` command.)

`netml learn` supports a great many additional options, documented by `netml learn --help`, `--help-algorithm` and `--help-param`, including:

* `--algorithm`: selection of model-training algorithms, such as One-Class Support Vector Machine (OCSVM), Kernel Density Estimation (KDE), Isolation Forest (IF) and Autoencoder (AE)
* `--param`: customization of model hyperparameters via YAML/JSON
* `--label`, `--pcap-normal` & `--pcap-abnormal`: optional labeling of traffic to enable post-training testing of the model

In the below examples, an OCSVM model is trained by demo traffic included in the library, and tested by labels in a CSV file, (both provided by the University of New Brunswick's [Intrusion Detection Systems dataset](https://www.unb.ca/cic/datasets/ids-2017.html)).

All of the below may be wrapped up into a single command via the CLI:

    netml learn --pcap=data/demo.pcap           \
                --label=data/demo.csv           \
                --output=out/OCSVM-results.dat

#### PCAP to features

To only extract features via the CLI:

    netml learn extract                         \
                --pcap=data/demo.pcap           \
                --label=data/demo.csv           \
                --feature=out/IAT-features.dat

Or in Python:

```python
from netml.pparser.parser import PCAP
from netml.utils.tool import dump_data

pcap = PCAP(
    'data/demo.pcap',
    flow_ptks_thres=2,
    random_state=42,
    verbose=10,
)

# extract flows from pcap
pcap.pcap2flows(q_interval=0.9)

# label each flow (optional)
pcap.label_flows(label_file='data/demo.csv')

# extract features from each flow via IAT
pcap.flow2features('IAT', fft=False, header=False)

# dump data to disk
dump_data((pcap.features, pcap.labels), out_file='out/IAT-features.dat')

# stats
print(pcap.features.shape, pcap.pcap2flows.tot_time, pcap.flow2features.tot_time)
```

#### Features to model

To train from already-extracted features via the CLI:

    netml learn train                           \
                --feature=out/IAT-features.dat  \
                --output=out/OCSVM-results.dat

Or in Python:

```python
from sklearn.model_selection import train_test_split

from netml.ndm.model import MODEL
from netml.ndm.ocsvm import OCSVM
from netml.utils.tool import dump_data, load_data

RANDOM_STATE = 42

# load data
(features, labels) = load_data('out/IAT-features.dat')

# split train and test sets
(
    features_train,
    features_test,
    labels_train,
    labels_test,
) = train_test_split(features, labels, test_size=0.33, random_state=RANDOM_STATE)

# create detection model
ocsvm = OCSVM(kernel='rbf', nu=0.5, random_state=RANDOM_STATE)
ocsvm.name = 'OCSVM'
ndm = MODEL(ocsvm, score_metric='auc', verbose=10, random_state=RANDOM_STATE)

# train the model from the train set
ndm.train(features_train)

# evaluate the trained model
ndm.test(features_test, labels_test)

# dump data to disk
dump_data((ocsvm, ndm.history), out_file='out/OCSVM-results.dat')

# stats
print(ndm.train.tot_time, ndm.test.tot_time, ndm.score)
```

For more examples, see the `examples/` directory in the source repository.


## Architecture

- `examples/`\
example code and datasets
- `src/netml/ndm/`\
detection models (such as OCSVM)
- `src/netml/pparser/`\
pcap processing (feature extraction) 
- `src/netml/utils/`\
common functions (such as `load_data` and `dump_data`)
- `tests/`\
test cases
- `LICENSE.txt`
- `manage.py`\
library development & management module
- `README.md`
- `setup.cfg`
- `setup.py`
- `tox.ini`


## To Do

Further work includes:

- Evaluate `pparser` performance on different pcaps
- Add test cases
- Add examples
- Add (generated) docs

We welcome any comments to make this tool more robust and easier to use!


## Development

Development dependencies may be installed via the `dev` extras (below assuming a source checkout):

    pip install --editable .[dev]

(Note: the installation flag `--editable` is also used above to instruct `pip` to place the source checkout directory itself onto the Python path, to ensure that any changes to the source are reflected in Python imports.)

Development tasks are then managed via [`argcmdr`](https://github.com/dssg/argcmdr) sub-commands of `manage …`, (as defined by the repository module `manage.py`), _e.g._:

    manage version patch -m "initial release of netml" \
           --build                                     \
           --release


## Acknowledgments

`netml` is based on the initial work of the ["Outlier Detection" library `odet`](https://github.com/Learn-Live/odet) 🙌

This work was authored by Kun Yang under the direction of Professor Samory
Kpotufe at Columbia University.


## Citation

    @article{yang2020comparative,
             title={A Comparative Study of Network Traffic Representations for Novelty Detection},
             author={Kun Yang and Samory Kpotufe and Nick Feamster},
             year={2020},
             eprint={2006.16993},
             archivePrefix={arXiv},
             primaryClass={cs.NI}
    }
