import csv
import sys
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    input_df = pd.read_csv(filename)
    evidence = input_df[['Administrative', 'Administrative_Duration', 'Informational',
           'Informational_Duration', 'ProductRelated', 'ProductRelated_Duration',
           'BounceRates', 'ExitRates', 'PageValues', 'SpecialDay', 'Month',
           'OperatingSystems', 'Browser', 'Region', 'TrafficType', 'VisitorType',
           'Weekend']]
    Month_map = {'Jan':0, 'Feb':1, 'Mar':2, 'Apr':3, 'May':4, 'Jun':5, 'Jul':6, 'Aug':7, 'Sep':8, 'Oct':9, 'Nov':10, 'Dec':11}
    VisitorType_map = {'Returning_Visitor':1, 'New_Visitor':0, 'Other':0}
    Weekend_map = {True:1, False:0}
    evidence['Month'] = evidence['Month'].map(Month_map)
    evidence.loc[evidence['Month'].isnull(),'Month'] = 12
    evidence['VisitorType'] = evidence['VisitorType'].map(VisitorType_map)
    evidence.loc[evidence['VisitorType'].isnull(),'VisitorType'] = 0
    evidence['Weekend'] = evidence['Weekend'].map(Weekend_map)
    evidence.loc[evidence['Weekend'].isnull(),'Weekend'] = 0

    evidence[['Administrative','Informational','ProductRelated','Month','OperatingSystems','Browser','Region','TrafficType','VisitorType','Weekend']] = evidence[['Administrative','Informational','ProductRelated','Month','OperatingSystems','Browser','Region','TrafficType','VisitorType','Weekend']].astype(int)
    evidence[['Administrative_Duration','Informational_Duration','ProductRelated_Duration','BounceRates','ExitRates','PageValues','SpecialDay']] = evidence[['Administrative_Duration','Informational_Duration','ProductRelated_Duration','BounceRates','ExitRates','PageValues','SpecialDay']].astype(float)

    evidence = evidence.values.tolist()
    labels = input_df['Revenue'].values.tolist()
    return (evidence, labels)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    knn_model = KNeighborsClassifier(n_neighbors = 1)
    knn_model.fit(evidence, labels)
    return knn_model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    sensitivity_list = []
    specificity_list = []
    max_row = min(len(labels),len(predictions))
    i = 0
    while i < max_row:
        if labels[i] == 1:
            if labels[i] == predictions[i]:
                sensitivity_list.append(1)
            else:
                sensitivity_list.append(0)

        if labels[i] == 0:
            if labels[i] == predictions[i]:
                specificity_list.append(1)
            else:
                specificity_list.append(0)                
        i = i +1

    if len(sensitivity_list) == 0:
        sensitivity = 1
    else:
        sensitivity = sum(sensitivity_list) / len(sensitivity_list) 

    if len(specificity_list) == 0:
        specificity = 1
    else:
        specificity = sum(specificity_list) / len(specificity_list)     

    return (sensitivity,specificity)


if __name__ == "__main__":
    main()
