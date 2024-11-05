import numpy as np
import pandas as pd
from pmdarima import auto_arima


class Forecast:
    def __init__(self):
        self.forecast_list = None

    def generate_initial_dataset(self, workload_generator, start_time='2024-09-10 00:00:00', periods=10, freq='30S'): #TODO use generators to automatically generate workload
        data = {
            'time': pd.date_range(start=start_time, periods=periods, freq=freq),
            'workload': [workload_generator.tick(i) for i in range(0, periods)]
            # 'workload': np.random.randint(50, 2000, size=periods)  # Valores aleatórios entre 50 e 200 (número de usuários)
        }
        return data



    # 2.Add new real data
    def update_dataset_realvalues(self, df,workloadgenerator, new_data=10, slot_length=30, freq='30S'): # TODO use generators to automatically generate workload
        """ Add new real data to the dataset. """
        last_data_slot = df.index[-1]
        new_slots = pd.date_range(start=last_data_slot + pd.DateOffset(seconds=slot_length), periods=new_data, freq=freq)
        new_data = [workloadgenerator.tick(i) for i in range(len(df), len(df)+new_data)]
        # new_data = np.random.randint(50, 2000, size=new_data)  # TODO use generators to automatically generate new workload
        new_data = pd.DataFrame({'workload': new_data}, index=new_slots)
        return pd.concat([df, new_data])

    # Predict the workload for a single dataframe (a single function in a cluster) NOTE: DONE
    def list_forecasted_data_poits(self, df, num_points_sample, num_forecast_points, slot_length=30, freq='30S'):
        # train ARIMA model for forecast
        self.forecast_list = []
        conf_list = []

        df_last_points = df.tail(num_points_sample)
        model = auto_arima(df_last_points['workload'],  start_p = 2, d = None, start_q = 2, max_p = 5, max_d = 2,
                       max_q = 5, start_P = 1, D = None, start_Q = 1, max_P = 2, max_D = 1, max_Q = 2,
                       max_order = 5, sp = 1, seasonal = True, stationary = False, information_criterion = 'aic',
                       alpha = 0.05, test = 'kpss', seasonal_test = 'ocsb', stepwise = True, n_jobs = 1,
                       start_params = None, trend = None, method = 'lbfgs', maxiter = 50,
                       offset_test_args = None, seasonal_test_args = None,
                       suppress_warnings = False, error_action = 'warn',
                       trace = False, random = False, random_state = None, n_fits = 10,
                       out_of_sample_size = 0, scoring = 'mse', scoring_args = None, with_intercept = True,
                       update_pdq = True, time_varying_regression = False, enforce_stationarity = True,
                       enforce_invertibility = True, simple_differencing = False, measurement_error = False,
                       mle_regression = True, hamilton_representation = False, concentrate_scale = False)
        # model = auto_arima(df_last_points['workload'], start_p=1, start_q=1, max_p=3, max_q=3, d=2, seasonal=False,
        # suppress_warnings=True)

        # predict the next points (e.g.: next 10 points)
        forecast, conf_int = model.predict(n_periods=num_forecast_points, return_conf_int=True)
        # forecast = np.round(forecast).astype(int)
        # generate times intervals for the forecasted values
        forecast_index = pd.date_range(start=df.index[-1] + pd.DateOffset(seconds=slot_length),
                                       periods=num_forecast_points, freq=freq)
        # Convert forecasted points into a data set for visualization
        forecast_df = pd.DataFrame({'forecast': forecast}, index=forecast_index)
        return forecast_df

    def lost(self):
        pass
