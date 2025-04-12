import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates


def calculate_ema(prices, N):
    alpha = 2 / (N + 1)
    ema_values = [prices[0]]

    for price in prices[1:]:
        ema_previous = ema_values[-1]
        ema_new = alpha * price + (1 - alpha) * ema_previous
        ema_values.append(ema_new)

    return ema_values


file_path = 'nvidia.csv'
data = pd.read_csv(file_path)
data['Data'] = pd.to_datetime(data['Data'])
data.set_index('Data', inplace=True)

ema26 = calculate_ema(data['Zamkniecie'].values, 26)
ema12 = calculate_ema(data['Zamkniecie'].values, 12)

macd = np.subtract(ema12, ema26)
signal = calculate_ema(macd, 9)

diff = np.sign(macd - signal)
crossings = np.where(np.diff(diff) != 0)[0]
cross_points_macd = []
cross_points_prices = []

for cross in crossings:
    x0, x1 = cross, cross + 1
    date_x1 = data.index[x1]
    cross_value_macd = macd[x1]
    cross_price = data['Zamkniecie'].iloc[x1]
    action = 'Kupno' if diff[x1] > 0 else 'Sprzedaż'

    cross_points_macd.append({
        'Data': date_x1.strftime('%Y-%m-%d'),
        'Akcja': action,
        'Wartość MACD': cross_value_macd
    })

    cross_points_prices.append({
        'Data': date_x1.strftime('%Y-%m-%d'),
        'Akcja': action,
        'Cena Akcji': cross_price
    })

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 14))

ax1.plot(data.index, data['Zamkniecie'], label='Cena zamknięcia', color='gray')
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax1.set_title('Cena zamknięcia cen walut USD/EUR')
ax1.legend(loc='upper left')
ax1.tick_params(axis='x', rotation=45)

ax2.plot(data.index, macd, label='MACD', color='blue')
ax2.plot(data.index, signal, label='Signal', color='red')
for point in cross_points_macd:
    color = 'green' if point['Akcja'] == 'Kupno' else 'red'
    ax2.scatter(pd.to_datetime(point['Data']), point['Wartość MACD'], color=color, zorder=5)

ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax2.set_title('MACD i Signal dla walut USD/EUR')
ax2.legend(['MACD', 'Signal'], loc='upper left')
ax2.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('usdeuro_chart.png')
plt.show()

#print("Punkty przecięcia z cenami akcji:")
#for point in cross_points_prices:
#    print(point)

kapital_poczatkowy = 1000
kapital = kapital_poczatkowy
ilosc_akcji = 0
transakcje = []

for i in range(len(cross_points_prices) - 1):
    punkt = cross_points_prices[i]
    if punkt['Akcja'] == 'Kupno':
        if cross_points_prices[i + 1]['Akcja'] == 'Sprzedaż':
            ilosc_akcji = kapital / punkt['Cena Akcji']
            kapital = 0
            transakcje.append(f"Kupno: {ilosc_akcji} akcji za {punkt['Cena Akcji']} na akcję")

        if ilosc_akcji > 0:
            kapital = ilosc_akcji * cross_points_prices[i + 1]['Cena Akcji']
            transakcje.append(f"Sprzedaż: {ilosc_akcji} akcji za {cross_points_prices[i + 1]['Cena Akcji']} na akcję")
            ilosc_akcji = 0

print(f"Kapitał początkowy: {kapital_poczatkowy}")
print(f"Kapitał końcowy: {kapital}")
print("Historia transakcji:")
for transakcja in transakcje:
    print(transakcja)
