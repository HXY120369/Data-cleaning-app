import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 设置随机种子以确保结果可重现
np.random.seed(42)

# 生成50条数据
data_size = 50

# 生成时间序列（假设每小时记录一次）
start_time = datetime.now()
time_series = [start_time + timedelta(hours=i) for i in range(data_size)]

# 生成温度数据（假设正常范围在20-30度之间，有一些随机波动）
base_temperature = 25
temperature_fluctuations = np.random.normal(0, 1.5, data_size)
temperatures = base_temperature + temperature_fluctuations

# 生成压力数据（假设正常范围在100-120 kPa之间，有一些随机波动）
base_pressure = 110
pressure_fluctuations = np.random.normal(0, 3, data_size)
pressures = base_pressure + pressure_fluctuations

# 偶尔添加一些异常值
for i in np.random.choice(data_size, 5):
    temperatures[i] += np.random.choice([-8, 8])  # 随机添加较大的波动
for i in np.random.choice(data_size, 5):
    pressures[i] += np.random.choice([-15, 15])  # 随机添加较大的波动

# 创建DataFrame
df = pd.DataFrame({
    '时间': time_series,
    '温度(°C)': temperatures.round(1),
    '压力(kPa)': pressures.round(1)
})

# 保存为Excel文件
excel_path = '设备数据_温度压力.xlsx'
df.to_excel(excel_path, index=False)

print(f"数据已成功生成并保存到 {excel_path}")