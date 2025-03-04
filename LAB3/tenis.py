import pandas as pd
import numpy as np
from sklearn import tree, metrics
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
from scipy.io import arff

data, meta = arff.loadarff('./tenis.arff')

df = pd.DataFrame(data)

label_encoders = {}
for col in df.columns:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

features = df.drop(columns=['Partida'])
target = df['Partida']

arvore = DecisionTreeClassifier(criterion='entropy').fit(features, target)

plt.figure(figsize=(10, 6.5))
tree.plot_tree(arvore, feature_names=features.columns, class_names=['Nao', 'Sim'], filled=True, rounded=True)
plt.show()

fig, ax = plt.subplots(figsize=(8, 6))
metrics.ConfusionMatrixDisplay.from_estimator(arvore, features, target, display_labels=['Nao', 'Sim'], values_format='d', ax=ax)
plt.show()
