from sklearn.model_selection import train_test_split

from netml.ndm.model import MODEL
from netml.ndm.ocsvm import OCSVM
from netml.utils.tool import dump_data, load_data

RANDOM_STATE = 42

# load data
(features, labels) = load_data('models/IAT-features.dat')

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
dump_data((ocsvm, ndm.history), out_file='models/OCSVM-results2.dat')

# stats
print(ndm.train.tot_time, ndm.test.tot_time, ndm.score)