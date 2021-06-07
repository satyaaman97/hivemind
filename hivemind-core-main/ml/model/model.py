from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from db_utils import Mongo
from joblib import dump
if __name__ == '__main__':
    mc = Mongo()
    coll = mc['WSB']['inputs']
    scaler = MinMaxScaler()
    inputs = list(coll.find().limit(10000))
    x = scaler.fit_transform([d['vector'] for d in inputs])

    y = [d['fitness'] for d in inputs]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.2)
    regr = MLPRegressor(hidden_layer_sizes=(100, 50, 20, 10), solver='lbfgs', activation="tanh",
                        max_iter=10000, verbose=True).fit(x_train, y_train)
    print(regr.score(x_test, y_test))
    dump(regr, "model.joblib")
