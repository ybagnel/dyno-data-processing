import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


version = "1.1.1"

pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 500)

test_type = "fuel_trim"
profile = "Profile 2"
curr_dir = Path.cwd()
path_to_folder = Path.joinpath(curr_dir, test_type)

# superflow_file = "superflow.csv"
# motec_file = "motec.csv"
# gas_file = "gas.csv"
# file_name = 'final_data.csv'

superflow_file = Path.joinpath(curr_dir, profile, test_type, "superflow.csv")
motec_file = Path.joinpath(curr_dir, profile, test_type, "motec.csv")
gas_file = Path.joinpath(curr_dir, profile, test_type, "gas.csv")
file_name = Path.joinpath(curr_dir, profile, test_type, 'final_data.csv')


def read_superflow():
    print("read_superflow")
    sf = pd.read_csv(superflow_file, skiprows=[1])
    sf = sf[['EngSpd',
             'ServoV',
             'EngPwr',
             'EngTrq',
             'LamAF1',
             'VolEff',
             'AirSum',
             'BoostP',
             'CoolIn',
             'CoolOt',
             'Exh_1 ',
             'Exh_2 ',
             'Exh_3 ',
             'Exh_4 ',
             'FulDif',
             'Batt_V',
             'Oil_P ']].copy()
    sf = sf.rename(columns={'EngSpd': 'EngineSpeed_RPM',
                            'ServoV': 'EngineLoad_%',
                            'EngPwr': 'EnginePower_HP',
                            'EngTrq': 'EngineTorque_lbs-ft',
                            'LamAF1': 'AirFuelRatio',
                            'VolEff': 'VolumetricEfficiency_%',
                            'AirSum': 'MassAirFlow_SCFM',
                            'BoostP': 'IntakeManifoldPressure_kPa',
                            'CoolIn': 'CoolantTempIn_C',
                            'CoolOt': 'CoolantTempOut_C',
                            'Exh_1 ': 'ExhaustTemp1_F',
                            'Exh_2 ': 'ExhaustTemp2_F',
                            'Exh_3 ': 'ExhaustTemp3_F',
                            'Exh_4 ': 'ExhaustTemp4_F',
                            'FulDif': 'FuelDifferential_lb/hr',
                            'Batt_V': 'BatteryValtage_V',
                            'Oil_P ': 'OilPressure_psi'})
    sf = sf.drop(sf.tail(1).index)
    sf = sf.astype(float)
    return sf


def read_motec():
    print("read_motec")
    motec = pd.read_csv(motec_file,
                        skiprows=[0, 1, 2, 3, 4,
                                  5, 6, 7, 8, 9,
                                  10, 11, 12, 13,
                                  15, 16, 17, 18])
    motec = motec[['Engine RPM',
                   'Throttle Pos',
                   'Manifold Pres',
                   'Air Temp Inlet',
                   'Ref Volts',
                   'Sync Volts',
                   'Fuel PW 1',
                   'Fuel PW 2',
                   'Fuel PW 3',
                   'Fuel PW 4',
                   'Ign Advance 1',
                   'Ign Advance 2',
                   'Ign Advance 3',
                   'Ign Advance 4']].copy()
    motec = motec.rename(columns={'Engine RPM': 'EngineSpeed_RPM',
                                  'Throttle Pos': 'ThrottlePosition_%',
                                  'Manifold Pres': 'IntakeManifoldPressure_kPa',
                                  'Air Temp Inlet': 'IntakeAirTemp_C',
                                  'Ref Volts': 'CrankshaftPosition_V',
                                  'Sync Volts': 'CamshaftPosition_V',
                                  'Fuel PW 1': 'FuelInjectorPulseWidth1_mSec',
                                  'Fuel PW 2': 'FuelInjectorPulseWidth2_mSec',
                                  'Fuel PW 3': 'FuelInjectorPulseWidth3_mSec',
                                  'Fuel PW 4': 'FuelInjectorPulseWidth4_mSec',
                                  'Ign Advance 1': 'IgnitionAdvance1_dBTC',
                                  'Ign Advance 2': 'IgnitionAdvance2_dBTC',
                                  'Ign Advance 3': 'IgnitionAdvance3_dBTC',
                                  'Ign Advance 4': 'IgnitionAdvance4_dBTC'})
    # motec = motec.drop([2],0)
    motec = motec.astype(float)
    return motec


def read_gas():
    print("read_gas")
    gas = pd.read_csv(gas_file, encoding='ISO-8859-1', skiprows=[0])
    gas = gas[['Time', 'CO2', 'CO', 'HC', 'O2', 'NOx']].copy()
    gas = gas.rename(columns={'CO2': 'CO2_%',
                              'CO': 'CO_%',
                              'HC': 'HC_ppm',
                              'O2': 'O2_%',
                              'NOx': 'NOx_ppm'})
    return gas


def match_data(sf, motec):
    print("match_data")
    error_tolerance = 90  # RPM
    calc_tolerance = 101  # RPM
    tolerance_range = 600
    while calc_tolerance > error_tolerance:
        motec = motec.iloc[1:].reset_index(drop=True)
        for i in range(0, tolerance_range):
            calc_tolerance += abs(motec['EngineSpeed_RPM'].iloc[i] - sf['EngineSpeed_RPM'].iloc[i])
        calc_tolerance = calc_tolerance / float(tolerance_range)
    print(f'Calculated tolerance: {calc_tolerance}')
    plt.plot(motec['EngineSpeed_RPM'])
    plt.plot(sf['EngineSpeed_RPM'])
    plt.show()
    good = input("Satisfied??? Press 'y' if YES, anything if NO. ")
    if good == 'y' or good == 'Y':
        return motec
    else:
        return match_data(sf, motec)


def add_time(df):
    print("add_time")
    num = []
    for i in range(0, len(df.index)):
        num.append(i * 0.2)
    df['Time_sec'] = num
    return df


def add_time_to_gas(gas_df, sf_df):
    print("add_time_to_gas")
    num = []
    temp_gas = pd.DataFrame(columns=gas_df.columns)
    # temp_gas.columns = gas_df.columns
    for i in range(0, len(sf_df.index)):
        num.append(i * 0.2)
        temp_gas.loc[i] = gas_df.loc[int(i / 5)]
    temp_gas['Time_sec'] = num
    return temp_gas


def merge_dfs(left_df, right_df):
    print("merge_dfs")
    temp_df = left_df.merge(right_df, left_on='Time_sec', right_on='Time_sec')
    return temp_df


def save_to_csv(df):
    print("save_to_csv")
    df.to_csv(file_name,
              index=False,
              columns=['Time_sec',
                       'EngineSpeed_RPM',
                       'EngineLoad_%',
                       'EnginePower_HP',
                       'EngineTorque_lbs-ft',
                       'AirFuelRatio',
                       'VolumetricEfficiency_%',
                       'MassAirFlow_SCFM',
                       'IntakeManifoldPressure_kPa',
                       'CoolantTempIn_C',
                       'CoolantTempOut_C',
                       'ExhaustTemp1_F',
                       'ExhaustTemp2_F',
                       'ExhaustTemp3_F',
                       'ExhaustTemp4_F',
                       'FuelDifferential_lb/hr',
                       'BatteryValtage_V',
                       'OilPressure_psi',
                       'ThrottlePosition_%',
                       'IntakeAirTemp_C',
                       'CrankshaftPosition_V',
                       'CamshaftPosition_V',
                       'FuelInjectorPulseWidth1_mSec',
                       'FuelInjectorPulseWidth2_mSec',
                       'FuelInjectorPulseWidth3_mSec',
                       'FuelInjectorPulseWidth4_mSec',
                       'IgnitionAdvance1_dBTC',
                       'IgnitionAdvance2_dBTC',
                       'IgnitionAdvance3_dBTC',
                       'IgnitionAdvance4_dBTC',
                       'CO2_%',
                       'CO_%',
                       'HC_ppm',
                       'O2_%',
                       'NOx_ppm'])


def main():
    superflow_data = read_superflow()
    motec_data = read_motec()
    gas_data = read_gas()
    motec_data = match_data(superflow_data, motec_data)
    # save_data(superflow_data, gas_data, motec_data)
    print("match complete")
    plt.plot(motec_data['EngineSpeed_RPM'])
    plt.plot(superflow_data['EngineSpeed_RPM'])
    plt.show()
    good = input("Final check, type 'good' to proceed. ")
    if good != "good":
        print("Exiting")
        exit()

    superflow_data.drop('EngineSpeed_RPM', axis=1, inplace=True)
    superflow_data.drop('IntakeManifoldPressure_kPa', axis=1, inplace=True)
    superflow_data = add_time(superflow_data)
    motec_data = add_time(motec_data)
    gas_data = add_time_to_gas(gas_data, superflow_data)
    combined_df = merge_dfs(superflow_data, motec_data)
    combined_df = merge_dfs(combined_df, gas_data)
    save_to_csv(combined_df)
    print("Post processing complete!!!")


if __name__ == "__main__":
    main()
