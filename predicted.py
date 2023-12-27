from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_transformer
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from sklearn import set_config

set_config(print_changed_only='True', display='diagram')

data = pd.DataFrame({'Law': jk['tr_main_law'].values.tolist(),
                     'Vote': jk["Hanjeza"].values.tolist(),
                     'reading': jk['reading'].values.tolist()})

X_train, X_test, y_train, y_test = train_test_split(
    data[['Law', 'reading']], data['Vote'], test_size=0.5)

ct = make_column_transformer(
    (CountVectorizer(), 'Law'), remainder='passthrough')

pipeline = make_pipeline(ct, DecisionTreeClassifier())
pipeline.fit(X_train, y_train)
pipeline.score(X_test, y_test)

p = pipeline.predict(data.loc[600:650,['Law', 'reading']])
