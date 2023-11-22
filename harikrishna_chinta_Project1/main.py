import pandas as pd
import numpy as np

#Read data and use the columns which are required.
cgm_excel=pd.read_csv('CGMData.csv',low_memory=False,usecols=['Date','Time','Sensor Glucose (mg/dL)'])
insulin_excel=pd.read_csv('InsulinData.csv',low_memory=False,usecols=['Date','Time','Alarm'])


#Merge Date and Time column into date_and_time and make that as an index to extract rows while calcuating metrics.
cgm_excel['date_and_time']=pd.to_datetime(cgm_excel['Date'] + ' ' + cgm_excel['Time'])
cgm_data_with_date_and_time = cgm_excel.set_index(pd.DatetimeIndex(cgm_excel['date_and_time']))
#print(cgm_data_with_date_and_time)

#Now do the same with Insulin data
#Merge Date and Time column into date_and_time and make that as an index to extract rows while calcuating metrics.
insulin_excel['date_and_time']=pd.to_datetime(insulin_excel['Date'] + ' ' + insulin_excel['Time'])
#insulin_data_with_date_and_time = insulin_excel.set_index(pd.DatetimeIndex(insulin_excel['date_and_time']))
#print(insulin_data_with_date_and_time)


#Filter the CGM Data with non-empty values.
cgm_data_with_non_empty_sensor_glucose_values = cgm_data_with_date_and_time.dropna(subset=['Sensor Glucose (mg/dL)'])
#print(cgm_data_with_non_empty_sensor_glucose_values)

#Filter the CGM Data with non-empty values.
#date_to_remove=cgm_data_with_date_and_time[cgm_data_with_date_and_time['Sensor Glucose (mg/dL)'].isna()]['Date'].unique()
#cgm_data_with_non_empty_sensor_glucose_values=cgm_data_with_date_and_time.set_index('Date').drop(index=date_to_remove).reset_index()

#Now find the date when the auto mode got started from the bottom.
auto_mode_start_date=insulin_excel.sort_values(by='date_and_time',ascending=True).loc[insulin_excel['Alarm']=='AUTO MODE ACTIVE PLGM OFF'].iloc[0]['date_and_time']
#print(auto_mode_start_date)

#Calculate 80% of dates filtering BEFORE THE SPLIT
#cgm_data_with_non_empty_sensor_glucose_values = cgm_data_with_non_empty_sensor_glucose_values.groupby('Date')['Sensor Glucose (mg/dL)'].count().where(lambda x:x>0.8*288).dropna().index.tolist()
eligible_rows = cgm_data_with_non_empty_sensor_glucose_values.groupby('Date')['Sensor Glucose (mg/dL)'].count().where(lambda x:x>=0.8*288).dropna().index.tolist()
cgm_data_with_non_empty_sensor_glucose_values = cgm_data_with_non_empty_sensor_glucose_values.loc[cgm_data_with_non_empty_sensor_glucose_values['Date'].isin(eligible_rows)]


#Split the actual CGM data into 2 data frames as per the auto mode start date and name them as auto data and manual data.
auto_mode_data=cgm_data_with_non_empty_sensor_glucose_values.loc[cgm_data_with_non_empty_sensor_glucose_values['date_and_time']>=auto_mode_start_date]
#print(auto_mode_data)

manual_mode_data = cgm_data_with_non_empty_sensor_glucose_values.loc[cgm_data_with_non_empty_sensor_glucose_values['date_and_time']<auto_mode_start_date]
#print(manual_mode_data)

#Calculate 80% of dates filtering AFTER THE SPLIT
#Now we will extract those dates for both Auto mode and Manual mode where the number of 5 minutes slots in a day are > 80% of the actual 288 5-minute slots
#dates_with_greater_than_80_percent_of_288_auto_mode = auto_mode_data.groupby('Date')['Sensor Glucose (mg/dL)'].count().where(lambda x:x>0.8*288).dropna().index.tolist()
#print(dates_with_greater_than_80_percent_of_288)
#auto_mode_data=auto_mode_data.loc[auto_mode_data['Date'].isin(dates_with_greater_than_80_percent_of_288_auto_mode)]
#print(auto_mode_data)

#dates_with_greater_than_80_percent_of_288_manual_mode = manual_mode_data.groupby('Date')['Sensor Glucose (mg/dL)'].count().where(lambda x:x>0.8*288).dropna().index.tolist()
#print(dates_with_greater_than_80_percent_of_288)
#manual_mode_data=manual_mode_data.loc[manual_mode_data['Date'].isin(dates_with_greater_than_80_percent_of_288_manual_mode)]
#print(manual_mode_data)


#Set the date_and_time as the new index to extract no:of rows by grouping with individual date
auto_mode_data=auto_mode_data.set_index('date_and_time')
manual_mode_data = manual_mode_data.set_index('date_and_time')
#print(auto_mode_data)
#print(manual_mode_data)


#Now calculate the % in Hyperglycemia (> 180 mg/dL) - daytime, overnight, whole day
hyperglycemia_for_dayTime_autoMode = (auto_mode_data.between_time('06:00:00','23:59:59')
                                                    .loc[auto_mode_data['Sensor Glucose (mg/dL)']>180]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

hyperglycemia_for_nightTime_autoMode = (auto_mode_data.between_time('00:00:00','05:59:59')  
                                                      .loc[auto_mode_data['Sensor Glucose (mg/dL)']>180]
                                                      .groupby('Date')['Sensor Glucose (mg/dL)']
                                                      .count()/288*100)

hyperglycemia_for_wholeDay_autoMode=(auto_mode_data.between_time('00:00:00','23:59:59')  
                                                   .loc[auto_mode_data['Sensor Glucose (mg/dL)']>180]
                                                   .groupby('Date')['Sensor Glucose (mg/dL)']
                                                   .count()/288*100)


#Now calculate the percentage in Hyperglycemia critical (> 250 mg/dL) - daytime, overnight, whole day
hyperglycemia_critical_for_dayTime_autoMode = (auto_mode_data.between_time('06:00:00','23:59:59')
                                                    .loc[auto_mode_data['Sensor Glucose (mg/dL)']>250]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

hyperglycemia_critical_for_nightTime_autoMode = (auto_mode_data.between_time('00:00:00','05:59:59')  
                                                      .loc[auto_mode_data['Sensor Glucose (mg/dL)']>250]
                                                      .groupby('Date')['Sensor Glucose (mg/dL)']
                                                      .count()/288*100)

hyperglycemia_critical_for_wholeTime_autoMode = (auto_mode_data.between_time('00:00:00','23:59:59')  
                                                   .loc[auto_mode_data['Sensor Glucose (mg/dL)'] > 250]
                                                   .groupby('Date')['Sensor Glucose (mg/dL)']
                                                   .count()/288*100)


#Now calculate percentage time in range (CGM >= 70 mg/dL and CGM <= 180 mg/dL), for daytime, overnight, whole day
CGM_for_dayTime_autoMode = (auto_mode_data.between_time('06:00:00','23:59:59')
                                                    .loc[(auto_mode_data['Sensor Glucose (mg/dL)']>=70) 
                                                    & (auto_mode_data['Sensor Glucose (mg/dL)']<=180)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

CGM_for_nightTime_autoMode = (auto_mode_data.between_time('00:00:00','05:59:59')  
                                                      .loc[(auto_mode_data['Sensor Glucose (mg/dL)']>=70) 
                                                    & (auto_mode_data['Sensor Glucose (mg/dL)']<=180)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

CGM_for_wholeDay_autoMode=(auto_mode_data.between_time('00:00:00','23:59:59')  
                                                   .loc[(auto_mode_data['Sensor Glucose (mg/dL)']>=70) 
                                                    & (auto_mode_data['Sensor Glucose (mg/dL)']<=180)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)


#Now calculate percentage in range secondary (CGM >= 70 mg/dL and CGM <= 150 mg/dL) - daytime, overnight, whole day
CGM_secondary_for_dayTime_autoMode = (auto_mode_data.between_time('06:00:00','23:59:59')
                                                    .loc[(auto_mode_data['Sensor Glucose (mg/dL)']>=70) 
                                                    & (auto_mode_data['Sensor Glucose (mg/dL)']<=150)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

CGM_secondary_for_nightTime_autoMode = (auto_mode_data.between_time('00:00:00','05:59:59')  
                                                      .loc[(auto_mode_data['Sensor Glucose (mg/dL)']>=70) 
                                                    & (auto_mode_data['Sensor Glucose (mg/dL)']<=150)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

CGM_secondary_for_wholeDay_autoMode=(auto_mode_data.between_time('00:00:00','23:59:59')  
                                                   .loc[(auto_mode_data['Sensor Glucose (mg/dL)']>=70) 
                                                    & (auto_mode_data['Sensor Glucose (mg/dL)']<=150)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)



#Now calcuate percentage in hypoglycemia level 1 (CGM < 70 mg/dL) - daytime, overnight, whole day
hypoglycemia_level1_for_dayTime_autoMode = (auto_mode_data.between_time('06:00:00','23:59:59')
                                                    .loc[(auto_mode_data['Sensor Glucose (mg/dL)']<70)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

hypoglycemia_level1_for_nightTime_autoMode = (auto_mode_data.between_time('00:00:00','05:59:59')  
                                                      .loc[(auto_mode_data['Sensor Glucose (mg/dL)']<70)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

hypoglycemia_level1_for_wholeDay_autoMode=(auto_mode_data.between_time('00:00:00','23:59:59')  
                                                   .loc[(auto_mode_data['Sensor Glucose (mg/dL)']<70)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)



#Now calcuate percentage in hypoglycemia level 2 (CGM < 54 mg/dL) - daytime, overnight, whole day
hypoglycemia_level2_for_dayTime_autoMode = (auto_mode_data.between_time('06:00:00','23:59:59')
                                                    .loc[(auto_mode_data['Sensor Glucose (mg/dL)']<54)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

hypoglycemia_level2_for_nightTime_autoMode = (auto_mode_data.between_time('00:00:00','05:59:59')  
                                                      .loc[(auto_mode_data['Sensor Glucose (mg/dL)']<54)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

hypoglycemia_level2_for_wholeDay_autoMode=(auto_mode_data.between_time('00:00:00','23:59:59')  
                                                   .loc[(auto_mode_data['Sensor Glucose (mg/dL)']<54)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)



#########     MANUAL MODE     #############
hyperglycemia_for_dayTime_manualMode = (manual_mode_data.between_time('06:00:00','23:59:59')
                                                    .loc[manual_mode_data['Sensor Glucose (mg/dL)']>180]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

hyperglycemia_for_nightTime_manualMode = (manual_mode_data.between_time('00:00:00','05:59:59')  
                                                      .loc[manual_mode_data['Sensor Glucose (mg/dL)']>180]
                                                      .groupby('Date')['Sensor Glucose (mg/dL)']
                                                      .count()/288*100)

hyperglycemia_for_wholeDay_manualMode=(manual_mode_data.between_time('00:00:00','23:59:59')  
                                                   .loc[manual_mode_data['Sensor Glucose (mg/dL)']>180]
                                                   .groupby('Date')['Sensor Glucose (mg/dL)']
                                                   .count()/288*100)


#Now calculate the percentage in Hyperglycemia critical (> 250 mg/dL) - daytime, overnight, whole day
hyperglycemia_critical_for_dayTime_manualMode = (manual_mode_data.between_time('06:00:00','23:59:59')
                                                    .loc[manual_mode_data['Sensor Glucose (mg/dL)']>250]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

hyperglycemia_critical_for_nightTime_manualMode = (manual_mode_data.between_time('00:00:00','05:59:59')  
                                                      .loc[manual_mode_data['Sensor Glucose (mg/dL)']>250]
                                                      .groupby('Date')['Sensor Glucose (mg/dL)']
                                                      .count()/288*100)

hyperglycemia_critical_for_wholeTime_manualMode = (manual_mode_data.between_time('00:00:00','23:59:59')  
                                                   .loc[manual_mode_data['Sensor Glucose (mg/dL)'] > 250]
                                                   .groupby('Date')['Sensor Glucose (mg/dL)']
                                                   .count()/288*100)


#Now calculate percentage time in range (CGM >= 70 mg/dL and CGM <= 180 mg/dL), for daytime, overnight, whole day
CGM_for_dayTime_manualMode = (manual_mode_data.between_time('06:00:00','23:59:59')
                                                    .loc[(manual_mode_data['Sensor Glucose (mg/dL)']>=70) 
                                                    & (manual_mode_data['Sensor Glucose (mg/dL)']<=180)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

CGM_for_nightTime_manualMode = (manual_mode_data.between_time('00:00:00','05:59:59')  
                                                      .loc[(manual_mode_data['Sensor Glucose (mg/dL)']>=70) 
                                                    & (manual_mode_data['Sensor Glucose (mg/dL)']<=180)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

CGM_for_wholeDay_manualMode=(manual_mode_data.between_time('00:00:00','23:59:59')  
                                                   .loc[(manual_mode_data['Sensor Glucose (mg/dL)']>=70) 
                                                    & (manual_mode_data['Sensor Glucose (mg/dL)']<=180)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)



#Now calculate percentage in range secondary (CGM >= 70 mg/dL and CGM <= 150 mg/dL) - daytime, overnight, whole day
CGM_secondary_for_dayTime_manualMode = (manual_mode_data.between_time('06:00:00','23:59:59')
                                                    .loc[(manual_mode_data['Sensor Glucose (mg/dL)']>=70) 
                                                    & (manual_mode_data['Sensor Glucose (mg/dL)']<=150)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

CGM_secondary_for_nightTime_manualMode = (manual_mode_data.between_time('00:00:00','05:59:59')  
                                                      .loc[(manual_mode_data['Sensor Glucose (mg/dL)']>=70) 
                                                    & (manual_mode_data['Sensor Glucose (mg/dL)']<=150)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

CGM_secondary_for_wholeDay_manualMode=(manual_mode_data.between_time('00:00:00','23:59:59')  
                                                   .loc[(manual_mode_data['Sensor Glucose (mg/dL)']>=70) 
                                                    & (manual_mode_data['Sensor Glucose (mg/dL)']<=150)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)



#Now calcuate percentage in hypoglycemia level 1 (CGM < 70 mg/dL) - daytime, overnight, whole day
hypoglycemia_level1_for_dayTime_manualMode = (manual_mode_data.between_time('06:00:00','23:59:59')
                                                    .loc[(manual_mode_data['Sensor Glucose (mg/dL)']<70)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

hypoglycemia_level1_for_nightTime_manualMode = (manual_mode_data.between_time('00:00:00','05:59:59')  
                                                      .loc[(manual_mode_data['Sensor Glucose (mg/dL)']<70)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

hypoglycemia_level1_for_wholeDay_manualMode=(manual_mode_data.between_time('00:00:00','23:59:59')  
                                                   .loc[(manual_mode_data['Sensor Glucose (mg/dL)']<70)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)



#Now calcuate percentage in hypoglycemia level 2 (CGM < 54 mg/dL) - daytime, overnight, whole day
hypoglycemia_level2_for_dayTime_manualMode = (manual_mode_data.between_time('06:00:00','23:59:59')
                                                    .loc[(manual_mode_data['Sensor Glucose (mg/dL)']<54)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

hypoglycemia_level2_for_nightTime_manualMode = (manual_mode_data.between_time('00:00:00','05:59:59')  
                                                      .loc[(manual_mode_data['Sensor Glucose (mg/dL)']<54)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)

hypoglycemia_level2_for_wholeDay_manualMode=(manual_mode_data.between_time('00:00:00','23:59:59')  
                                                   .loc[(manual_mode_data['Sensor Glucose (mg/dL)']<54)]
                                                    .groupby('Date')['Sensor Glucose (mg/dL)']
                                                    .count()/288*100)



#Now calculate mean for all the metrics in Auto mode as well as Manual mode
result = pd.DataFrame({"Overnight Percentage time in hyperglycemia (CGM > 180 mg/dL)":[hyperglycemia_for_nightTime_manualMode.mean(axis=0),hyperglycemia_for_nightTime_autoMode.mean(axis=0)],
                           "Overnight percentage of time in hyperglycemia critical (CGM > 250 mg/dL)":[hyperglycemia_critical_for_nightTime_manualMode.mean(axis=0), hyperglycemia_critical_for_nightTime_autoMode.mean(axis=0)],
                           "Overnight percentage time in range (CGM >= 70 mg/dL and CGM <= 180 mg/dL)":[CGM_for_nightTime_manualMode.mean(axis=0), CGM_for_nightTime_autoMode.mean(axis=0)],
                           "Overnight percentage time in range secondary (CGM >= 70 mg/dL and CGM <= 150 mg/dL)":[CGM_secondary_for_nightTime_manualMode.mean(axis=0), CGM_secondary_for_nightTime_autoMode.mean(axis=0)],
                           "Overnight percentage time in hypoglycemia level 1 (CGM < 70 mg/dL)":[hypoglycemia_level1_for_nightTime_manualMode.mean(axis=0), hypoglycemia_level1_for_nightTime_autoMode.mean(axis=0)],
                           "Overnight percentage time in hypoglycemia level 2 (CGM < 54 mg/dL)":[hypoglycemia_level2_for_nightTime_manualMode.mean(axis=0), hypoglycemia_level2_for_nightTime_autoMode.mean(axis=0)],
                           "Daytime Percentage time in hyperglycemia (CGM > 180 mg/dL)":[hyperglycemia_for_dayTime_manualMode.mean(axis=0), hyperglycemia_for_dayTime_autoMode.mean(axis=0)],
                           "Daytime percentage of time in hyperglycemia critical (CGM > 250 mg/dL)":[hyperglycemia_critical_for_dayTime_manualMode.mean(axis=0), hyperglycemia_critical_for_dayTime_autoMode.mean(axis=0)],
                           "Daytime percentage time in range (CGM >= 70 mg/dL and CGM <= 180 mg/dL)":[CGM_for_dayTime_manualMode.mean(axis=0), CGM_for_dayTime_autoMode.mean(axis=0)],
                           "Daytime percentage time in range secondary (CGM >= 70 mg/dL and CGM <= 150 mg/dL)":[CGM_secondary_for_dayTime_manualMode.mean(axis=0), CGM_secondary_for_dayTime_autoMode.mean(axis=0)],
                           "Daytime percentage time in hypoglycemia level 1 (CGM < 70 mg/dL)":[hypoglycemia_level1_for_dayTime_manualMode.mean(axis=0), hypoglycemia_level1_for_dayTime_autoMode.mean(axis=0)],
                           "Daytime percentage time in hypoglycemia level 2 (CGM < 54 mg/dL)":[hypoglycemia_level2_for_dayTime_manualMode.mean(axis=0), hypoglycemia_level2_for_dayTime_autoMode.mean(axis=0)],
                           "Whole Day Percentage time in hyperglycemia (CGM > 180 mg/dL)":[hyperglycemia_for_wholeDay_manualMode.mean(axis=0), hyperglycemia_for_wholeDay_autoMode.mean(axis=0)],
                           "Whole day percentage of time in hyperglycemia critical (CGM > 250 mg/dL)":[hyperglycemia_critical_for_wholeTime_manualMode.mean(axis=0), hyperglycemia_critical_for_wholeTime_autoMode.mean(axis=0)],
                           "Whole day percentage time in range (CGM >= 70 mg/dL and CGM <= 180 mg/dL)":[CGM_for_wholeDay_manualMode.mean(axis=0), CGM_for_wholeDay_autoMode.mean(axis=0)],
                           "Whole day percentage time in range secondary (CGM >= 70 mg/dL and CGM <= 150 mg/dL)":[CGM_secondary_for_wholeDay_manualMode.mean(axis=0), CGM_secondary_for_wholeDay_autoMode.mean(axis=0)],
                           "Whole day percentage time in hypoglycemia level 1 (CGM < 70 mg/dL)":[hypoglycemia_level1_for_wholeDay_manualMode.mean(axis=0), hypoglycemia_level1_for_wholeDay_autoMode.mean(axis=0)],
                           "Whole Day percentage time in hypoglycemia level 2 (CGM < 54 mg/dL)":[hypoglycemia_level2_for_wholeDay_manualMode.mean(axis=0), hypoglycemia_level2_for_wholeDay_autoMode.mean(axis=0)]},
                           index=['manual_mode','auto_mode'])
                                  
result = result.fillna(0)

result.to_csv('Results.csv',header=False,index=False)


