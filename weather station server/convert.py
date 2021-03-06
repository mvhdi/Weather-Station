#!/usr/bin/python

#**************************************************************
#* Notes: Instantiates all DataConverter subclasses and calls *
#* instances' safe_process methods. 						  *
#**************************************************************

import DataConverters as dc
from errors import debug

#this list holds the converter object corresponding to every outgoing data field
#when new fields are added, a new subclass of DataConverter should be defined and added here
#the order of this list is inconsequential unless there is a converter that requires the last value of
#another, in which case the dependent one should go after its dependency

all_converters = [
	dc.mux_current(),							
	dc.mux_temperature(),							
	dc.Peet_wind_rate(),							
	dc.Peet_wind_multl(),
	dc.Peet_windlo(),
	dc.Peet_wind_multh(),
	dc.Peet_windhi(),
	dc.Peet_vduce(),
	dc.Peet_wind_speed(),
	dc.Peet_winddir(),
	dc.Peet_wind_direction(),
	dc.Inspeed_wind_direction(),
	dc.Hydreon_current(),
	dc.Hydreon_temperature(),
	dc.Hydreon_range_setting(),
	dc.Hydreon_low_sense(),
	dc.Hydreon_medium_sense(),
	dc.Hydreon_high_sense(),
	dc.Hydreon_rain_amount(),
	dc.sky_sensor_current(),
	dc.sky_swiper_CW_current(),
	dc.sky_swiper_CCW_current(),
	dc.sky_dark_reading(),
	dc.sky_bright_reading(),
	dc.sky_IR_temperature(),
	dc.sky_sensor_status(),
	dc.sky_Hall_sensor(),
	dc.sway_X40_reading(),
	dc.sway_X1_reading(),
	dc.sway_Y1_reading(),
	dc.sway_Y40_reading(),
	dc.sway_sensor_temperature(),
	dc.sway_sensor_Vss(),
	dc.sway_Z_offset(),
	dc.sway_Z50_reading(),

	dc.lightning_current(),
	dc.lightning_UV_count(),
	dc.lightning_high_voltage(),
	dc.lightning_3001_lux(),
	dc.lightning_Skyscan_current(),
	dc.lightning_Skyscan_LEDs(),
	dc.lightning_Skyscan_flash_time(),
	dc.lightning_Skyscan_alarms(),
	dc.lightning_OPT101_baseline(),
	dc.lightning_OPT101_north(),
	dc.lightning_OPT101_south(),
	dc.lightning_OPT101_east(),
	dc.lightning_OPT101_west(),
	dc.lightning_OPT101_zenith(),
	dc.lightning_thunder(),
	dc.lightning_flag(),
	dc.lightning_UVA_UVB(),
	dc.lightning_OPT_temperature(),

	dc.solar_box_temperature(),
	dc.solar_pyran_combined(),
	dc.solar_par_combined(),
	dc.solar_UV_combined(),
	dc.solar_gold_grid_east(),
	dc.solar_gold_grid_west(),
	dc.solar_Decagon_horizontal(),
	dc.solar_Decagon_tilted(),
	dc.solar_frost(),
	dc.solar_bud(),
	dc.solar_globe_combined(),
	dc.solar_current(),
	dc.solar_voltage(),
	dc.solar_IR_ground_temperature(),

	dc.MetOne_LED_current(),
	dc.MetOne_pulsewidth(),
	dc.MetOne_ticks_count(),

	dc.fuses_Arbcam_current(),
	dc.fuses_Arbcam_voltage(),
	dc.fuses_5V6_voltage(),
	dc.fuses_mux_current(),
	dc.fuses_lightning_current(),
	dc.fuses_solar_DAQ_current(),
	dc.fuses_fluxgate_current(),
	dc.fuses_triaxial_current(),
	dc.fuses_future_current(),
	dc.fuses_flag(),
	dc.fuses_warn(),
	dc.fuses_go_up(),
	dc.fuses_monitor(),
	dc.fuses_Arbcam_mode(),
	dc.fuses_fault_status(),

	dc.power_solar_panel_current(),
	dc.power_solar_panel_voltage(),
	dc.pm_battery_current(),
	dc.pm_battery_voltage(),
	dc.power_current_into_5V6(),
	dc.power_voltage_into_5V6(),
	dc.power_5V6_load_current(),
	dc.power_5V6_load_voltage(),
	dc.pm_box_temperature(),
	dc.power_Arbcam_dcdc_input_current(),
	dc.power_Arbcam_dcdc_input_voltage(),
	dc.power_Arbcam_current(),
	dc.power_Arbcam_voltage(),
	dc.power_battery_temperature(),
	dc.power_128K_battery_voltage(),
	dc.power_RTC_battery_voltage(),
	dc.power_RTD_30ft_temperature(),
	dc.power_hail_peak(),
	dc.power_hail_average(),
	dc.pm_status(),
	dc.power_OVP_cycles(),
	dc.power_OVP_voltage(),
	dc.power_hail_sensor_temperature(),
	dc.power_hail_sensor_hits(),
	dc.power_box_humidity(),

	dc.geiger_ticks(),
	dc.geiger_high_volts(),
	dc.geiger_current(),
	dc.geiger_temperature(),
	dc.geiger_status(),

	dc.vortex_avg_speed(),
	dc.vortex_wind_gust(),
	dc.vortex_calc_mph(),

	dc.rain_drip_code(),
	dc.rain_bucket(),
	dc.rain_rate(),
	dc.rain_ten_min_dry(),
	dc.rain_battery_voltage(),

	dc.RTD_1K_combined(),
	dc.RTD_100_combined(),
	dc.RTD_Davis_combined(),
	dc.RH_sensor_1(),
	dc.RH_sensor_2(),
	dc.outer_shield_LM335(),
	dc.middle_shield_LM335(),
	dc.inner_shield_LM335(),
	dc.bowl_LM335(),
	dc.ambient_temp_LM335(),
	dc.IR_snow_depth(),
	dc.temp_head_fan_airflow(),
	dc.temp_head_fan_voltage(),
	dc.temp_head_fan_current(),
	dc.PTB_combined(),
	dc.AD_temperature(),

	dc.fan_voltage(),
	dc.fan_current(),
	dc.fan_speed(),
	dc.TS4200_current(),
	dc.RF_link_current(),
	dc.box_humidity(),
	dc.ground_temperature(),
	dc.snow_depth_sonic(),
	dc.barometric_pressure(),
	dc.ten_enclosure_temp(),
	dc.ten_circuit_current(),
	dc.ten_RTD_temperature(),
	dc.RH_Precon(),
	dc.Temperature_Precon(),
	dc.RH_Honeywell(),
	dc.ten_avg_wind_speed(),
	dc.ten_instant_wind_speed(),
	dc.ten_wind_direction(),

	dc.power_100WA_voltage(),
	dc.power_100WA_current(),
	dc.power_100WB_voltage(),
	dc.power_100WB_current(),
	dc.power_50W_voltage(),
	dc.power_50W_current(),
	dc.power_20WA_voltage(),
	dc.power_20WA_current(),
	dc.power_load_voltage(),
	dc.power_load_current(),
	dc.power_battery_voltage(),
	dc.power_battery_current(),
	dc.power_solar_voltage(),
	dc.power_solar_current(),
	dc.power_20WB_voltage(),
	dc.power_20WB_current(),
	dc.power_fan_current_A(),
	dc.power_heater_current_A(),
	dc.power_battery_temperature_A(),
	dc.power_cabinet_temperature(),
	dc.power_MPPT_temperature(),
	dc.power_5C_voltage(),
	dc.power_5DAQ_voltage(),
	dc.power_5DAQ_current(),
	dc.power_VTOP_voltage(),
	dc.power_VTOP_current(),
	dc.power_VAUX_voltage(),
	dc.power_VAUX_current(),
	dc.power_DAQ_input_current(),
	dc.power_battery_temperature_B(),
	dc.power_box_temperature(),
	dc.power_heater_current_B(),
	dc.power_fan_current_B(),
	dc.power_status(),
	dc.power_enclosure_humidity(),
	dc.power_fault_status(),

	dc.soil_temp_1_below(),
	dc.soil_temp_2_below(),
	dc.soil_temp_3_below(),
	dc.soil_temp_4_below(),
	dc.soil_temp_5_below(),
	dc.soil_temp_6_below(),
	dc.soil_temp_7_below(),
	dc.soil_temp_8_below(),
	dc.soil_temp_10_below(),
	dc.soil_temp_12_below(),
	dc.soil_temp_20_below(),
	dc.soil_temp_30_below(),
	dc.soil_temp_40_below(),
	dc.soil_temp_48_below(),

	dc.soil_moist_b2(),
	dc.soil_moist_b4(),
	dc.soil_moist_b6(),
	dc.soil_moist_b8(),
	dc.soil_moist_b10(),
	dc.soil_moist_b15(),
	dc.soil_moist_b20(),
	dc.soil_moist_b40(),

	dc.temp_1_above(),
	dc.temp_2_above(),
	dc.temp_3_above(),
	dc.temp_4_above(),
	dc.temp_5_above(),
	dc.temp_7_above(),
	dc.temp_9_above(),
	dc.temp_11_above(),
	dc.temp_13_above(),
	dc.temp_15_above(),

	dc.soil_flux(),
	dc.soil_electronics_temp(),
	dc.soil_electronics_Vref(),
	dc.soil_spare(),

	dc.geiger_burst_count(),
	dc.geiger_burst_time(),
	dc.barometric_temperature(),

	dc.sway_X1(),
	dc.sway_X2(),
	dc.sway_X3(),
	dc.sway_X4(),
	dc.sway_X5(),
	dc.sway_X6(),
	dc.sway_X7(),
	dc.sway_X8(),
	dc.sway_X9(),
	dc.sway_X10(),
	dc.sway_X11(),
	dc.sway_X12(),
	dc.sway_X13(),
	dc.sway_X14(),
	dc.sway_X15(),
	dc.sway_X16(),
	dc.sway_X17(),
	dc.sway_X18(),
	dc.sway_X19(),
	dc.sway_X20(),
	dc.sway_X21(),
	dc.sway_X22(),
	dc.sway_X23(),
	dc.sway_X24(),
	dc.sway_X25(),
	dc.sway_X26(),
	dc.sway_X27(),
	dc.sway_X28(),
	dc.sway_X29(),
	dc.sway_X30(),
	dc.sway_X31(),
	dc.sway_X32(),
	dc.sway_X33(),
	dc.sway_X34(),
	dc.sway_X35(),
	dc.sway_X36(),
	dc.sway_X37(),
	dc.sway_X38(),
	dc.sway_X39(),
	dc.sway_X40(),
	dc.sway_Y1(),
	dc.sway_Y2(),
	dc.sway_Y3(),
	dc.sway_Y4(),
	dc.sway_Y5(),
	dc.sway_Y6(),
	dc.sway_Y7(),
	dc.sway_Y8(),
	dc.sway_Y9(),
	dc.sway_Y10(),
	dc.sway_Y11(),
	dc.sway_Y12(),
	dc.sway_Y13(),
	dc.sway_Y14(),
	dc.sway_Y15(),
	dc.sway_Y16(),
	dc.sway_Y17(),
	dc.sway_Y18(),
	dc.sway_Y19(),
	dc.sway_Y20(),
	dc.sway_Y21(),
	dc.sway_Y22(),
	dc.sway_Y23(),
	dc.sway_Y24(),
	dc.sway_Y25(),
	dc.sway_Y26(),
	dc.sway_Y27(),
	dc.sway_Y28(),
	dc.sway_Y29(),
	dc.sway_Y30(),
	dc.sway_Y31(),
	dc.sway_Y32(),
	dc.sway_Y33(),
	dc.sway_Y34(),
	dc.sway_Y35(),
	dc.sway_Y36(),
	dc.sway_Y37(),
	dc.sway_Y38(),
	dc.sway_Y39(),
	dc.sway_Y40(),

	dc.fluxgate_T1(),
	dc.fluxgate_X1(),
	dc.fluxgate_Y1(),
	dc.fluxgate_Z1(),
	dc.fluxgate_T2(),
	dc.fluxgate_X2(),
	dc.fluxgate_Y2(),
	dc.fluxgate_Z2(),
	dc.fluxgate_T3(),
	dc.fluxgate_X3(),
	dc.fluxgate_Y3(),
	dc.fluxgate_Z3(),
	dc.fluxgate_T4(),
	dc.fluxgate_X4(),
	dc.fluxgate_Y4(),
	dc.fluxgate_Z4(),
	dc.fluxgate_T5(),
	dc.fluxgate_X5(),
	dc.fluxgate_Y5(),
	dc.fluxgate_Z5(),
	dc.fluxgate_T6(),
	dc.fluxgate_X6(),
	dc.fluxgate_Y6(),
	dc.fluxgate_Z6(),
	dc.fluxgate_T7(),
	dc.fluxgate_X7(),
	dc.fluxgate_Y7(),
	dc.fluxgate_Z7(),
	dc.fluxgate_T8(),
	dc.fluxgate_X8(),
	dc.fluxgate_Y8(),
	dc.fluxgate_Z8(),
	dc.fluxgate_T9(),
	dc.fluxgate_X9(),
	dc.fluxgate_Y9(),
	dc.fluxgate_Z9(),
	dc.fluxgate_T10(),
	dc.fluxgate_X10(),
	dc.fluxgate_Y10(),
	dc.fluxgate_Z10(),
	dc.fluxgate_T11(),
	dc.fluxgate_X11(),
	dc.fluxgate_Y11(),
	dc.fluxgate_Z11(),
	dc.fluxgate_T12(),
	dc.fluxgate_X12(),
	dc.fluxgate_Y12(),
	dc.fluxgate_Z12(),
	dc.fluxgate_T13(),
	dc.fluxgate_X13(),
	dc.fluxgate_Y13(),
	dc.fluxgate_Z13(),
	dc.fluxgate_T14(),
	dc.fluxgate_X14(),
	dc.fluxgate_Y14(),
	dc.fluxgate_Z14(),
	dc.fluxgate_current(),
	dc.fluxgate_temperature(),
	dc.fluxgate_xset(),
	dc.fluxgate_yset(),
	dc.fluxgate_zset(),
	dc.fluxgate_flag(),

	dc.triaxial_T1(),
	dc.triaxial_X1(),
	dc.triaxial_Y1(),
	dc.triaxial_Z1(),
	dc.triaxial_T2(),
	dc.triaxial_X2(),
	dc.triaxial_Y2(),
	dc.triaxial_Z2(),
	dc.triaxial_T3(),
	dc.triaxial_X3(),
	dc.triaxial_Y3(),
	dc.triaxial_Z3(),
	dc.triaxial_T4(),
	dc.triaxial_X4(),
	dc.triaxial_Y4(),
	dc.triaxial_Z4(),
	dc.triaxial_T5(),
	dc.triaxial_Y5(),
	dc.triaxial_X5(),
	dc.triaxial_Z5(),
	dc.triaxial_T6(),
	dc.triaxial_X6(),
	dc.triaxial_Y6(),
	dc.triaxial_Z6(),
	dc.triaxial_T7(),
	dc.triaxial_X7(),
	dc.triaxial_Y7(),
	dc.triaxial_Z7(),
	dc.triaxial_T8(),
	dc.triaxial_X8(),
	dc.triaxial_Y8(),
	dc.triaxial_Z8(),
	dc.triaxial_T9(),
	dc.triaxial_X9(),
	dc.triaxial_Y9(),
	dc.triaxial_Z9(),
	dc.triaxial_T10(),
	dc.triaxial_X10(),
	dc.triaxial_Y10(),
	dc.triaxial_Z10(),
	dc.triaxial_T11(),
	dc.triaxial_X11(),
	dc.triaxial_Y11(),
	dc.triaxial_Z11(),
	dc.triaxial_T12(),
	dc.triaxial_X12(),
	dc.triaxial_Y12(),
	dc.triaxial_Z12(),
	dc.triaxial_T13(),
	dc.triaxial_X13(),
	dc.triaxial_Y13(),
	dc.triaxial_Z13(),
	dc.triaxial_T14(),
	dc.triaxial_X14(),
	dc.triaxial_Y14(),
	dc.triaxial_Z14(),
	dc.triaxial_T15(),
	dc.triaxial_X15(),
	dc.triaxial_Y15(),
	dc.triaxial_Z15(),
	dc.triaxial_T16(),
	dc.triaxial_X16(),
	dc.triaxial_Y16(),
	dc.triaxial_Z16(),
	dc.triaxial_T17(),
	dc.triaxial_X17(),
	dc.triaxial_Y17(),
	dc.triaxial_Z17(),
	dc.triaxial_T18(),
	dc.triaxial_X18(),
	dc.triaxial_Y18(),
	dc.triaxial_Z18(),
	dc.triaxial_T19(),
	dc.triaxial_X19(),
	dc.triaxial_Y19(),
	dc.triaxial_Z19(),
	dc.triaxial_T20(),
	dc.triaxial_X20(),
	dc.triaxial_Y20(),
	dc.triaxial_Z20(),
	dc.triaxial_current(),
	dc.triaxial_volts(),
	dc.triaxial_temperature()
	]


def process_all():									#this function loops through all converters and calls safe_process on them.
	debug("process_all called; calling safe_process of all data converters...")
	for converter in all_converters:				#it is called from main.py after data is read.
		converter.safe_process()					#safe_process (defined in DataConverters.py) handles getting raw data from the reader, converting it, responding to
													#it, sending alerts about it, and finally passing it to the outputter

def reset_all_flags():								#resets flags for all converters. called from main.py daily.
	debug("reset_all_flags called; resetting all data converter error flags...")
	for converter in all_converters:
		converter.reset_flags()