import os

from pandas import datetime
from matplotlib import pyplot
import numpy
from pandas import read_csv
import math
from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error


def create_dataset(dataset, look_back=1):
    dataX, dataY = [], []
    for i in range(len(dataset)-look_back-1):
        a = dataset[i:(i+look_back), 0]
        dataX.append(a)
        dataY.append(dataset[i + look_back, 0])
    return numpy.array(dataX), numpy.array(dataY)


def parser(x):
    return datetime.strptime('200' + x, '%Y-%m')


def get_plot(path=None, path_dohod=None):
    image_dohod = None
    image_rashod = None
    logger_dohod = {}
    logger_rashod = {}
    if path:
        image_rashod, logger_rashod = fit_model(path, "График суммы расходов")
    if path_dohod:
        image_dohod, logger_dohod = fit_model(path_dohod, "График суммы доходов")
    return image_rashod, logger_rashod, image_dohod, logger_dohod


def fit_model(path, name):
    numpy.random.seed(7)
    # load the dataset
    dataframe = read_csv(path, usecols=[1], engine='python', skipfooter=3)
    dataset = dataframe.values
    dataset = dataset.astype('float32')
    # normalize the dataset
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(dataset)
    # split into train and test sets
    train_size = int(len(dataset) * 0.66)
    test_size = len(dataset) - train_size
    train, test = dataset[0:train_size, :], dataset[train_size:len(dataset), :]
    # reshape into X=t and Y=t+1
    look_back = 1
    trainX, trainY = create_dataset(train, look_back)
    testX, testY = create_dataset(test, look_back)
    # reshape input to be [samples, time steps, features]
    trainX = numpy.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
    testX = numpy.reshape(testX, (testX.shape[0], 1, testX.shape[1]))
    # create and fit the LSTM network
    model = Sequential()
    model.add(LSTM(4, input_shape=(1, look_back)))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(trainX, trainY, epochs=100, batch_size=1, verbose=2, use_multiprocessing=True)
    # make predictions
    trainPredict = model.predict(trainX)
    testPredict = model.predict(testX)
    # invert predictions
    trainPredict = scaler.inverse_transform(trainPredict)
    trainY = scaler.inverse_transform([trainY])
    testPredict = scaler.inverse_transform(testPredict)
    testY = scaler.inverse_transform([testY])
    # calculate root mean squared error
    trainScore = math.sqrt(mean_squared_error(trainY[0], trainPredict[:, 0]))
    print('Train Score: %.2f RMSE' % trainScore)
    testScore = math.sqrt(mean_squared_error(testY[0], testPredict[:, 0]))
    print('Test Score: %.2f RMSE' % testScore)
    # shift train predictions for plotting
    trainPredictPlot = numpy.empty_like(dataset)
    trainPredictPlot[:, :] = numpy.nan
    trainPredictPlot[0:len(trainPredict), :] = trainPredict
    # shift test predictions for plotting
    testPredictPlot = numpy.empty_like(dataset)
    testPredictPlot[:, :] = numpy.nan
    testPredictPlot[len(trainPredict) + (look_back * 2): len(dataset) - 2, :] = testPredict

    fig, ax = pyplot.subplots()
    dataset_logger = scaler.inverse_transform(dataset)
    dataset_logger = dataset_logger[0: len(dataset) - 2]
    ax.plot(dataset_logger, label='Обучающая выборка')
    ax.plot(trainPredictPlot, color='red', label='Предикт LTSM на обучающей выборке')
    ax.plot(testPredictPlot, color='black', label='Предикт LTSM на тестовом отрезке')

    ax.grid(True)
    ax.set_xlabel(u'Месяца')
    ax.set_ylabel(u'Сумма в млн. руб.')
    ax.set_title(name)
    ax.legend(loc='best', frameon=False)
    fig.savefig('image.png')
    image = load_file('image.png')
    logger = []

    dates = read_csv(path, usecols=[0], engine='python', skipfooter=3, parse_dates=[0], date_parser=parser)
    # dates_value = dates.values
    for i in range(len(dataset_logger)):
        if i < len(dataset_logger) - 2:
            logger.append({
                'date': datetime.fromisoformat(str(dates.Month[i])),
                'value': dataset_logger[i],
                'predict_value': ''
            })
    for i in range(0, len(trainPredict)):
        logger[i]['predict_value'] = trainPredictPlot[i][0]
    for i in range(len(trainPredict) + (look_back * 2), len(dataset_logger) - 2):
        logger[i]['predict_value'] = testPredictPlot[i][0]
    return image, logger


def load_file(path):
    file = open(path, 'rb')
    image = file.read()
    file.close()
    file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'image.png')
    os.remove(file)
    return image
