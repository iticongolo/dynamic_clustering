import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pmdarima import auto_arima
import matplotlib.dates as mdates
from generators import SinGen, RampGen
import time

# # 1. Exemplo de dados de vendas mensais
# # Criar uma série temporal de vendas fictícias
# data = {
#     'Mês': pd.date_range(start='2020-01-01', periods=24, freq='MS'),  # Início de cada mês
#     'Vendas': [120, 130, 125, 135, 140, 145, 150, 160, 155, 165, 170, 180,
#                190, 200, 210, 205, 215, 220, 230, 240, 245, 250, 260, 270]
# }
#
# # Criar um DataFrame
# df = pd.DataFrame(data)
# df.set_index('Mês', inplace=True)
#
# # 2. Visualizar a série temporal
# # print(df.head())
# print(df)
# df.plot()
# plt.title("Vendas Mensais")
# plt.xlabel("Mês")
# plt.ylabel("Vendas")
# plt.show()
#
# # 3. Ajustar o modelo Auto-ARIMA
# # Seasonal=False: Não consideramos sazonalidade aqui. Altere para True se os dados forem sazonais.
# model = auto_arima(df['Vendas'],
#                    seasonal=False,  # Se os dados forem sazonais, coloque True
#                    trace=True,      # Para mostrar o progresso do ajuste
#                    suppress_warnings=True,
#                    stepwise=True)   # Método stepwise para encontrar os melhores parâmetros
#
# # Exibir o resumo do modelo
# print(model.summary())
#
# # 4. Fazer previsões
# # Prever os próximos 6 meses
# n_periods = 6
# forecast, conf_int = model.predict(n_periods=n_periods, return_conf_int=True)
#
# # Criar um índice de datas para as previsões
# forecast_index = pd.date_range(start=df.index[-1] + pd.DateOffset(1), periods=n_periods, freq='MS')
#
# # Converter a previsão em um DataFrame para visualização
# forecast_df = pd.DataFrame({'Previsão': forecast}, index=forecast_index)
#
# # 5. Visualizar as previsões junto com os dados reais
# plt.plot(df['Vendas'], label='Vendas reais')
# plt.plot(forecast_df, label='Previsão', color='red')
# plt.fill_between(forecast_index, conf_int[:, 0], conf_int[:, 1], color='red', alpha=0.3)
# plt.title('Vendas Reais e Previsão ARIMA')
# plt.xlabel('Mês')
# plt.ylabel('Vendas')
# plt.legend()
# plt.show()
#

# g0 = SinGen(500, 700, 200); g0.setName("SN1 - App 1")
# g1 = RampGen(10, 800); g1.setName("RP1 - App 2")
# g2 = SinGen(500, 700, 200); g2.setName("SN1 - App 3")
# g3 = RampGen(10, 800); g3.setName("RP1 - App 4")
# g4 = SinGen(500, 700, 200); g4.setName("SN1 - App 5")
# g5 = RampGen(10, 800); g5.setName("RP1 - App 6")
# g6 = SinGen(500, 700, 200); g6.setName("SN1 - App 7")

def generate_initial_dataset(workloadgenerator, start_time='2024-09-10 00:00:00', periods=10, freq='30S'): #TODO use generators to automatically generate workload
    data = {
        'time': pd.date_range(start=start_time, periods=periods, freq=freq),
        'workload': [workloadgenerator.tick(i) for i in range(0, periods)]
        # 'workload': np.random.randint(50, 2000, size=periods)  # Valores aleatórios entre 50 e 200 (número de usuários)
    }
    return data


# 2.Add new real data
def update_dataset_real_values(df,workloadgenerator, new_data=10, slot_length=30, freq='30S'): # TODO use generators to automatically generate workload
    """ Add new real data to the dataset. """
    last_data_slot = df.index[-1]
    new_slots = pd.date_range(start=last_data_slot + pd.DateOffset(seconds=slot_length), periods=new_data, freq=freq)
    new_data = [workloadgenerator.tick(i) for i in range(len(df), len(df)+new_data)]
    # new_data = np.random.randint(50, 2000, size=new_data)  # TODO use generators to automatically generate new workload
    new_data = pd.DataFrame({'workload': new_data}, index=new_slots)
    return pd.concat([df, new_data])


# df_c1 = update_dataset_realvalues(df_c1, gen_sin_f0_c0, new_data=10)

# get the last 100 point for prediction
# df_last_100 = df_c1.tail(100)

# print the last 100 data points
# print("\nThe last 100 data points used for prediction:")
# print(df_last_100)



def list_forecasted_data_poits(dfs, num_points_sample, num_forecast_points,slot_length=30,freq='30S' ):
    # train ARIMA model for forecast
    forecast_list=[]
    conf_list=[]
    f_names=[]
    for df in dfs:
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
        # model = auto_arima(df_last_points['workload'], seasonal=True, trace=True, suppress_warnings=True, stepwise=True, max_p=4, max_q=3, max_P=1, max_Q=1)
        # model = auto_arima(df_last_points['workload'], start_p=1, start_q=1, max_p=3, max_q=3, d=2, seasonal=False,
        # suppress_warnings=True)

        # predict the next points (e.g.: next 10 points)
        forecast, conf_int = model.predict(n_periods=num_forecast_points, return_conf_int=True)
        # generate times intervals for the forecasted values
        forecast_index = pd.date_range(start=df.index[-1] + pd.DateOffset(seconds=slot_length), periods=num_forecast_points, freq=freq)
        # Convert forecasted points into a data set for visualization
        forecast_df = pd.DataFrame({'forecast': forecast}, index=forecast_index)
        forecast_list.append(forecast_df)
        conf_list.append(conf_int)
        f_names.append(df.name)
    return forecast_list, conf_list, f_names


start_time = time.time()
gen_c1 = SinGen(20, 50, 110)
gen_c1.name = "SIN20,50,110"
gen_c2 = RampGen(1, 1200)
gen_c2.name = "RAMP1,400"
gen_c3 = RampGen(2, 260)
gen_c3.name = "RAMP2,260"
data_c1 = generate_initial_dataset(gen_c1, periods=1000)
data_c2 = generate_initial_dataset(gen_c2, periods=1000)
data_c3 = generate_initial_dataset(gen_c3, periods=1000)
# create initial dataframe
df_c1 = pd.DataFrame(data_c1)
df_c1.name=gen_c1.name
df_c2 = pd.DataFrame(data_c2)
df_c2.name=gen_c2.name
df_c3 = pd.DataFrame(data_c3)
df_c3.name=gen_c3.name

df_c1.set_index('time', inplace=True)
df_c2.set_index('time', inplace=True)
df_c3.set_index('time', inplace=True)

# print initial dataframe
print("Workload generated by Sin model:")
print(df_c1, gen_c1.name)

print("Workload generated by Ramp model:")
print(df_c2)

print("Total data:")
print(len(df_c1))
df_list = [df_c1, df_c2, df_c3]
# df_list = [df_c2]
forecast_results, conf_int_list, fr_names = list_forecasted_data_poits(df_list, 80, 30)

i=0
for fr in forecast_results:
    print(fr)
    plt.plot(df_list[i].index, df_list[i]['workload'], label='Real data')
    plt.plot(fr.index, fr['forecast'], label='Forcast', color='red')
    plt.fill_between(fr.index, conf_int_list[i][:, 0], conf_int_list[i][:, 1], color='pink', alpha=0.3)
    plt.legend()
    plt.title(f'Workload Forecast in the next 15 min {fr_names[i]}')
    print(fr_names[i])
    plt.xlabel('time(s)')
    plt.ylabel('workload')
    # Access the current axis
    ax = plt.gca()

    # Set major ticks to every 30 seconds
    ax.xaxis.set_major_locator(mdates.SecondLocator(interval=600))

    # Set formatter to display only minutes and seconds
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))

    # Reduce overlap by setting the maximum number of ticks and rotating labels
    plt.gcf().autofmt_xdate()  # Auto format the x-axis labels

    # Rotate and format the x-axis labels
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    plt.clf()  # Clears the current plot
    i=i+1
end_time = time.time()
duration=end_time-start_time
print(f'--------------------------------------------')
print(f'Prediction Duration {duration} seconds')
