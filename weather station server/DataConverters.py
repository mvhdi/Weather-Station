#!/usr/bin/python

#**************************************************************
#* Notes: Holds all equations for converting raw data,        *
#* organized by block and number. Also holds response logic   *
#* for all measurements. If necessary to modify how data is   *
#* converted or responded to, modifying this file should be   *
#* sufficient.                                                *
#**************************************************************

import errors
import Config
from handleData import DataMissingError, NoSuchLabelError

from decimal import Decimal as dec
import decimal
import traceback
from math import pow, sqrt


#===================================================================================================================
#													DATACONVERTER CLASS DEFINITION
#===================================================================================================================
# The DataConverter class holds logic that is applicable to all (or nearly all) outgoing data fields. There is one 
# subclass of DataConverter per outgoing field, responsible for gathering the necessary raw data from the reader, 
# converting it, and passing the converted data to the outputter. Along the way they will check that the data is in 
# the correct range and handle whatever errors arise.

class DataConverter(object):
	command_error = False
	reader = None
	outputter = None
	suppress_range_check = False
#-------------------------------------------------------------------------------------------------------------------
#													CONSTRUCTOR:
# Initializes DataConverter object. Should be added to in subclass definitions.
	def __init__(self):
		self.raw_label = type(self).__name__
		self.conv_label = type(self).__name__
		self.last_val = Config.ERROR_VAL
		self.lower_bound = dec("-Infinity")
		self.upper_bound = dec("Infinity")
		self.status_error = False
		self.range_error = False
		self.process_error = False
		self.dec_places_round = 4
		self.report_out_of_range_data = True

#-------------------------------------------------------------------------------------------------------------------
#													UPDATE READER/OUTPUTTER:
# Updates saved reader and outputter for all DataConverter subclasses. To be used on WeatherScheduler initialization.
	@staticmethod
	def set_in_out(reader=None, outputter=None):
		DataConverter.reader = reader
		DataConverter.outputter = outputter

#-------------------------------------------------------------------------------------------------------------------
#													PROCESS RAW DATA:
# Converts raw data (as a string) into converted data (as a Decimal). Must be overwritten in subclass definitions.
# No need for error handling -- this is done in safe_process for ease and replicability.
	def process(self):
		return Config.ERROR_VAL

#-------------------------------------------------------------------------------------------------------------------
#													RESPOND TO DATA:
# Takes action -- i.e., issues commands to PIC and sends notifications -- in response to data. Should be overwritten
# in subclass definitions requiring a response.
	def respond(self, converteddata):
		pass

#-------------------------------------------------------------------------------------------------------------------
#													CHECK RANGE OF DATA:
# Confirms that converted is within range specified in subclass definition. If not, alerts and replaces data with
# error value. For some subclasses, it may be necessary to overwrite this with more complex logic, but in the case
# where one of the bounds is not required, just use +/-infinity in __init__().
	def check_range(self,converteddata):
		if type(converteddata) is str:
			return converteddata

		if self.suppress_range_check:
			return converteddata

		if self.lower_bound <= converteddata <= self.upper_bound:
			if self.range_error:
				errors.error(self.conv_label + " range error resolved, reported value is back within bounds.")
			self.range_error = False
			return converteddata
		elif not self.range_error:
			errors.error("OUT OF RANGE ERROR: " + self.conv_label + " reported value of " + str(converteddata))
			self.range_error = True

		if not self.report_out_of_range_data:
			return Config.ERROR_VAL
		else:
			return converteddata

#-------------------------------------------------------------------------------------------------------------------
#													SAFE_PROCESS:
# This method provides a framework that calls all user-written methods and handles errors. Should probably not be 
# overwritten in subclass definitions. The idea is that only this needs to be called and all relevant things will
# be taken care of.
	def safe_process(self):
		try:
			if self.raw_label != "N/A": 
				data = DataConverter.reader.get(self.raw_label)
			else:
				data = Config.ERROR_VAL
			data = self.process(data)
			if data != Config.ERROR_VAL:
				try:
					data = round(data, self.dec_places_round)
				except TypeError:
					pass #in cases of the data not being a number or no rounding desired
			data = self.check_range(data)
			if self.process_error:
				self.process_error = False
				errors.error(self.conv_label + " process error resolved. Data processed successfully.")
		except DataMissingError as e:
			errors.debug(e)
			data = Config.ERROR_VAL
		except:
			if not self.process_error:
				errors.error("PROCESS ERROR: " + self.conv_label + " unable to process received data" + 
					". Probably received or expected wrong data type. Assume error continues until fixed. Error messsage: " + 
					traceback.format_exc(Config.TRACEBACK_LIMIT))
			self.process_error = True
			data = Config.ERROR_VAL
		DataConverter.outputter.receive(self.conv_label, data)
		self.respond(data)
		self.last_val = data

#-------------------------------------------------------------------------------------------------------------------
#													RESET FLAGS:
# Resets error flags so reminder notifications will be sent. Called daily.
	def reset_flags(self):
		self.process_error = False
		self.range_error = False
		self.status_error = False
		if self.suppress_range_check:
			errors.info("Reminder: range check suppressed for " + self.conv_label)
			
#===================================================================================================================
#...................................................................................................................
#...................................................................................................................
#...................................................TOP.............................................................
#...................................................................................................................
#...................................................................................................................
#===================================================================================================================
#
#===================================================================================================================
#													GEIGER BLOCK
#===================================================================================================================
# Raw data format: dec5 ticks, 9, dec4 volts, dec4 amps, 9, dec5 tempr, 9, hex2 status, 13
#-------------------------------------------------------------------------------------------------------------------
#													TICKS:
# This is the number of Geiger tube ticks that occur in 1 minute.
# Typical background levels are around 100-120.
# Requires no conversion or response.

class geiger_ticks(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 5
		self.upper_bound = 2000
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = int(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													VOLTS:
# This is the high voltage for the geiger tube.
# To convert from raw voltage, divide by 1024, multiply by 5, and multiply by 250.
# The result is in volts.

class geiger_high_volts(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 800
		self.upper_bound = 900
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = ((dec(rawdata)/1024)*5)*250
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													AMPS:
# This is the current drawn by the geiger circuit.
# Each volt of raw data corresponds to 16.66 mA actual load current.
# The result is in mA.

class geiger_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 10
		self.upper_bound = 55
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/60)*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TEMPERATURE:
# This is the temperature inside the geiger circuit in degrees F.

class geiger_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -20
		self.upper_bound = 100
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)*dec("0.4"))-dec("273.16"))*dec("1.8"))+32
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													STATUS:
# This is status of the geiger circuit. It is sent as a byte:
# 		0th bit == 1 indicates under-voltage condition.
# 		1st bit == 1 indicates over-voltage condition.
# 		2nd bit == 1 indicates high-current condition.
# 		3rd bit == 1 indicates over-current condition and geiger high-voltage shutdown.

class geiger_status(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 15
		self.dec_places_round = "N/A"

	def process(self, rawdata):
		binary = bin(int(rawdata))[2:].zfill(4)
		binarylength = len(binary)
		bit0 = int(binary[binarylength-1])
		bit1 = int(binary[binarylength-2])
		bit2 = int(binary[binarylength-3])
		bit3 = int(binary[binarylength-4])
		converted = ""
		if bit0:
			converted += "under voltage, "
		if bit1:
			converted += "over voltage, "
		if bit2:
			converted += "high current, "
		if bit3:
			converted += "shutdown"
		converted = converted.rstrip(', ')
		if converted == "":
			converted = "OK"
			self.status_error = False
		elif not self.status_error:
			errors.error("Geiger status reported " + converted)
			self.status_error = True
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													BURST COUNT:
# Indicates max count of ticks within the last minute.

class geiger_burst_count(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 25
		self.dec_places_round = 1

	def process(self, rawdata):
		return int(rawdata)

#-------------------------------------------------------------------------------------------------------------------
#													BURST TIME:
# Indicates a 3 second max count period packet within a minute.

class geiger_burst_time(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 21
		self.dec_places_round = 1

	def process(self, rawdata):
		return int(rawdata)

#===================================================================================================================
#													VORTEX BLOCK
#===================================================================================================================
# 
#-------------------------------------------------------------------------------------------------------------------
#													AVERAGE SPEED:
# Average windspeed over last minute measured by vortex anemometer. Result is in mph.

class vortex_avg_speed(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 120
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = (dec(rawdata)*25)/600
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													GUST:
# Peak gust over last minute measured by vortex anemometer in mph.
class vortex_wind_gust(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 120
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = (dec(rawdata)*25)/600
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													CALCULATED WIND SPEED:
class vortex_calc_mph(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 120
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)/dec(600)
		return converted

#===================================================================================================================
#													RAIN GAUGE BLOCK
#===================================================================================================================
#
#-------------------------------------------------------------------------------------------------------------------
#													DRIP CODE:
# 
class rain_drip_code(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.dec_places_round = "N/A"

	def process(self, rawdata):
		converted = str(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													INCHES OF RAIN:
# Rain received in a day. Result is in inches.
class rain_bucket(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 1500
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = dec(rawdata)/dec(100)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													INCHES OF RAIN:
# Lower numbers indicate faster rainfall.
class rain_rate(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 200
		self.upper_bound = 65536
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = int(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													INCHES OF RAIN:
# Time in minutes since last bucket tip to nearest ten minutes.
class rain_ten_min_dry(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 28000
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*dec(10)
		return int(converted)

#-------------------------------------------------------------------------------------------------------------------
#													BATTERY VOLTAGE:
# Result is in volts.
class rain_battery_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.conv_label = "rain_battery_voltage"
		self.lower_bound = 2.8
		self.upper_bound = 4.6
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = ((dec(rawdata)/1024)*dec("2.5"))*2
		return converted


#===================================================================================================================
#													TEMP HEAD BLOCK
#===================================================================================================================
# 
#-------------------------------------------------------------------------------------------------------------------
#													RTD_1K_COMBINED
class RTD_1K_combined(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.raw_label = "N/A"
		self.lower_bound = -40
		self.upper_bound = 105
		self.dec_places_round = 4

	def process(self, rawdata):
		upper = hex(int(DataConverter.reader.get("RTD_1K_upper")))
		middle = hex(int(DataConverter.reader.get("RTD_1K_middle")))
		lower = hex(int(DataConverter.reader.get("RTD_1K_lower")))
		combined = int(upper[2:] + middle[2:] + lower[2:], base = 16)
		r = dec(((((dec(combined) / 8388608)*dec("2.5"))/dec("0.0005"))/10))
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2))+ ((dec("1.0241")*dec(pow(10,-6)))*(r**3))
		converted = (t*dec((9/5))) - dec("459.67") 
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													RTD_100_COMBINED
class RTD_100_combined(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.raw_label = "N/A"
		self.lower_bound = -40
		self.upper_bound = 105
		self.dec_places_round = 4

	def process(self, rawdata):
		upper = hex(int(DataConverter.reader.get("RTD_100_upper")))
		middle = hex(int(DataConverter.reader.get("RTD_100_middle")))
		lower = hex(int(DataConverter.reader.get("RTD_100_lower")))
		combined = int(upper[2:] + middle[2:] + lower[2:], base = 16)
		r = dec((((dec(combined) / 8388608)*dec("2.5"))/dec("0.0005")))
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2))+ ((dec("1.0241")*dec(pow(10,-6)))*(r**3))
		converted = (t*dec((9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													RTD_DAVIS_COMBINED
class RTD_Davis_combined(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.raw_label = "N/A"
		self.lower_bound = -40
		self.upper_bound = 105
		self.dec_places_round = 4

	def process(self, rawdata):
		upper = hex(int(DataConverter.reader.get("RTD_Davis_upper")))
		middle = hex(int(DataConverter.reader.get("RTD_Davis_middle")))
		lower = hex(int(DataConverter.reader.get("RTD_Davis_lower")))
		combined = int(upper[2:] + middle[2:] + lower[2:], base = 16)
		r = dec(((((dec(combined) / 8388608)*dec("2.5"))/dec("0.0005"))/10))
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2))+ ((dec("1.0241")*dec(pow(10,-6)))*(r**3))
		converted = (t*dec((9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													RH_SENSOR_1:
# Result is humidity in %. Sensor is HIH-5030.
class RH_sensor_1(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 15
		self.upper_bound = 101
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = dec(rawdata)*dec("32.2") - dec("25.8") 
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													RH_SENSOR_2:
# Result is humidity in %. Sensor is HIH-5030.
class RH_sensor_2(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 15
		self.upper_bound = 101
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = dec(rawdata)*dec("32.2") - dec("25.8") 
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													OUTER_SHIELD_LM335:
# Result is in degrees Fahrenheit.
class outer_shield_LM335(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 110
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((((dec(rawdata)/131072)*10)-dec("2.7316"))*180)+32
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													MIDDLE_SHIELD_LM335:
# Result is in degrees Fahrenheit.
class middle_shield_LM335(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 100
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((((dec(rawdata)/131072)*10)-dec("2.7316"))*180)+32
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													INNER_SHIELD_LM335:
# Result is in degrees Fahrenheit.
class inner_shield_LM335(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 100
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((((dec(rawdata)/131072)*10)-dec("2.7316"))*180)+32
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													BOWL_LM335:
# Result is in degrees Fahrenheit.
class bowl_LM335(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 100
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((((dec(rawdata)/131072)*10)-dec("2.7316"))*180)+32
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													AMBIENT_TEMP_LM335:
# Result is in degrees Fahrenheit.
class ambient_temp_LM335(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 100
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((((dec(rawdata)/131072)*10)-dec("2.7316"))*180)+32
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													IR_SNOW_DEPTH:
# L is height above ground in cm, result is snow depth in inches
class IR_snow_depth(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 30
		self.dec_places_round = 2

	def process(self, rawdata):
		l = 100 #height above ground in cm
		converted = (l-((dec("10650.08")*(((dec(rawdata)/65536)*5)**(dec("-0.935"))))-10))*dec("0.393701")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TEMP_HEAD_FAN_AIRFLOW:
# Result is in arbitrary units.
class temp_head_fan_airflow(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0.1
		self.upper_bound = 0.25
		self.dec_places_round = 4

	def process(self, rawdata):
		converted = (dec(rawdata)/131072)*5
		return converted


#-------------------------------------------------------------------------------------------------------------------
#													TEMP_HEAD_FAN_VOLTAGE:
# Result is in volts.
class temp_head_fan_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.conv_label = "temp_head_fan_voltage"
		self.lower_bound = 5
		self.upper_bound = 13
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = ((dec(rawdata)/131072)*5)*5
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TEMP_HEAD_FAN_CURRENT:
# Result is in volts.
class temp_head_fan_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 200
		self.upper_bound = 475
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = ((dec(rawdata)/131072)*5)/6
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													PTB_CONVERTED:
# Result is in inches of mercury.
class PTB_combined(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.raw_label = "N/A"
		self.lower_bound = 25
		self.upper_bound = 32
		self.dec_places_round = 4

	def process(self, rawdata):
		upper = hex(int(DataConverter.reader.get("PTB_upper")))
		middle = hex(int(DataConverter.reader.get("PTB_middle")))
		lower = hex(int(DataConverter.reader.get("PTB_lower")))
		combined = int(upper[2:] + middle[2:] + lower[2:], base = 16)
		converted = (((dec(combined)/16777216)*600)+500)*dec("0.0295299831")
		return converted


#-------------------------------------------------------------------------------------------------------------------
#													AD_TEMPERATURE:
# Result is in degrees Fahrenheit.
class AD_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 100
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = (((((dec(rawdata)/131072)*10)-dec("2.7316"))*100)*dec("1.8"))+32
		return converted

#===================================================================================================================
#													FAN BLOCK
#===================================================================================================================
# 
#-------------------------------------------------------------------------------------------------------------------
#													FAN_VOLTAGE:
# Result is in volts.
class fan_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 5
		self.upper_bound = 13
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = ((dec(rawdata)/1024)*5)*5
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													FAN_CURRENT:
# Result is in milliamps.
class fan_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 200
		self.upper_bound = 475
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/6)*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													FAN_SPEED:
# Result is in rpm.
class fan_speed(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1200
		self.upper_bound = 1900
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = int(rawdata) * 20
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TS4200_CURRENT:
# Result is in mA.
class TS4200_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 100
		self.upper_bound = 150
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/6)*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													RF_LINK_CURRENT:
# Result is in mA.
class RF_link_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 100
		self.upper_bound = 250
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/6)*1000
		return converted


#-------------------------------------------------------------------------------------------------------------------
#													BOX_HUMIDITY:
# Sensor directly outputs humidity 0-100%.
class box_humidity(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 100
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													GROUND_TEMPERATURE:
# Result is in degrees Fahrenheit.
class ground_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -45
		self.upper_bound = 130
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = (((dec(rawdata)/50)-dec("273.16"))*dec("1.8"))+32
		return converted

#===================================================================================================================
#													TEN FOOT BLOCK
#===================================================================================================================
#

#-------------------------------------------------------------------------------------------------------------------
#													SNOW_DEPTH_SONIC:
# 
class snow_depth_sonic(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 75
		self.upper_bound = 120
		self.dec_places_round = 2
		self.height_of_sensor = 114

	def process(self, rawdata):
		converted = dec(str(self.height_of_sensor)) - (dec(rawdata)/dec("25.4"))
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													BAROMETRIC_PRESSURE:
# Long and complicated procedure
class barometric_pressure(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 26
		self.upper_bound = 32
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													BAROMETRIC_TEMPERATURE:
# Long and complicated procedure
class barometric_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 110
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted


#-------------------------------------------------------------------------------------------------------------------
#													TEN_ENCLOSURE_TEMP:
# Result is in degrees Fahrenheit.
class ten_enclosure_temp(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -20
		self.upper_bound = 115
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = ((((dec(rawdata)*4)/10)-dec("273.16"))*dec("1.8"))+32
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TEN_CIRCUIT_CURRENT:
# Result is in mA.
class ten_circuit_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 5
		self.upper_bound = 40
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/60)*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TEN_RTD_TEMPERATURE
# Result is in mA.
class ten_RTD_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 110
		self.dec_places_round = 2

	def process(self, rawdata):
		r = (((dec(rawdata)/65536)*dec("4.096"))/dec("0.0005"))/10
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2)) + (dec("1.0241")*dec(pow(10,-6))*(r**3))
		converted = (t*dec(9/5))-dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													RH_PRECON:
# Result is humidity rounded to 1 decimal place.
class RH_Precon(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 5
		self.upper_bound = 100
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/131072)*dec("4.0886"))*100)/5
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TEMPERATURE_PRECON:
# Result is temperature (F) rounded to 1 decimal place.
class Temperature_Precon(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = ((((dec(rawdata)/131072)*dec("4.0886"))/dec("0.02137"))-22)*dec("0.818")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													RH_HONEYWELL:
# Result is humidity rounded to 1 decimal place.
class RH_Honeywell(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 5
		self.upper_bound = 100
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (dec(rawdata)*dec("32.2")) - dec("25.8")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TEN_AVG_WIND_SPEED
# Peet Bros.-time of 1 rotation of the cups, counts of 30.5 usec pulses
class ten_avg_wind_speed(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "N/A"
		self.upper_bound = "N/A"
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TEN_INSTANT_WIND_SPEED
# time that magnet sensor is closed, counts of 30.5 usec pulses
class ten_instant_wind_speed(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "N/A"
		self.upper_bound = "N/A"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TEN_WIND_DIRECTION
# time that magnet sensor is closed, counts of 30.5 usec pulses
class ten_wind_direction(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "N/A"
		self.upper_bound = "N/A"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted

#===================================================================================================================
#													POWER SUPPLY BLOCK
#===================================================================================================================
#
#-------------------------------------------------------------------------------------------------------------------
#													POWER_100WA_VOLTAGE:
# Result is in volts.
class power_100WA_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 19
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (dec(rawdata)/dec("1000")) * dec("5.02")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_100WA_CURRENT:
# Result is in mA.
class power_100WA_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 6000
		self.dec_places_round = 0
	def process(self, rawdata):
		converted = ((dec(rawdata) - dec("2500"))/dec("167"))*dec("1000")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_100WB_VOLTAGE:
# Result is in volts.
class power_100WB_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 19
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (dec(rawdata)/dec("1000")) * dec("5.02")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_100WB_CURRENT:
# Result is in mA.
class power_100WB_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 6000
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = ((dec(rawdata) - dec("2500"))/dec("167"))*dec("1000")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_50W_VOLTAGE:
# Result is in volts.
class power_50W_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 19
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (dec(rawdata)/dec("1000")) * dec("5.02")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_50W_CURRENT:
# Result is in mA.
class power_50W_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 3100
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = ((dec(rawdata) - dec("2500"))/dec("185"))*dec("1000")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_20WA_VOLTAGE:
# Result is in volts.
class power_20WA_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 19
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (dec(rawdata)/dec("1000")) * dec("5.02")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_20WA_CURRENT:
# Result is in mA.
class power_20WA_current(DataConverter):
	suppress_range_check = True
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 1400
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = ((dec(rawdata) - dec("2500"))/dec("185"))*dec("1000")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_LOAD_VOLTAGE:
# Result is in volts.
class power_load_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 15
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (dec(rawdata)/dec("1000")) * dec("5.02")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_LOAD_CURRENT:
# Result is in mA.
class power_load_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 2
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)/dec("1.2")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_BATTERY_VOLTAGE:
# Result is in volts.
class power_battery_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 19
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (dec(rawdata)/dec("1000")) * dec("5.02")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_BATTERY_CURRENT:
# Result is in mA.
class power_battery_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -15000
		self.upper_bound = 2000
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = ((dec(rawdata) - dec("2500"))/dec("83"))*dec("1000")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_SOLAR_VOLTAGE:
# Result is in volts.
class power_solar_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 19
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (dec(rawdata)/dec("1000")) * dec("5.02")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_SOLAR_CURRENT:
# Result is in mA.
class power_solar_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 15000
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = ((dec(rawdata) - dec("2500"))/dec("83"))*dec("1000")
		return converted  

#-------------------------------------------------------------------------------------------------------------------
#													POWER_20WB_VOLTAGE:
# Result is in volts.
class power_20WB_voltage(DataConverter):
	
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 19
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (dec(rawdata)/dec("1000")) * dec("5.02")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_20WB_CURRENT:
# Result is in mA.
class power_20WB_current(DataConverter):
	suppress_range_check = True
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 1400
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = ((dec(rawdata) - dec("2500"))/dec("185"))*dec("1000")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_FAN_CURRENT_A:
# Result is in mA.
class power_fan_current_A(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 50
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = dec(rawdata)/dec("60")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_HEATER_CURRENT_A:
# Result is in mA.
class power_heater_current_A(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 650
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = dec(rawdata)/dec("6")
		return converted


#-------------------------------------------------------------------------------------------------------------------
#													POWER_BATTERY_TEMPERATURE_A:
# Result is temperature in degrees Fahrenheit.
class power_battery_temperature_A(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 50
		self.upper_bound = 100
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = ((dec(rawdata)-dec("2731.6"))*dec(".18")) + dec("32")
		return converted
#-------------------------------------------------------------------------------------------------------------------
#													POWER_CABINET_TEMPERATURE:
# Result is temperature in degrees Fahrenheit.
class power_cabinet_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 10
		self.upper_bound = 100
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = ((dec(rawdata)-dec("2731.6"))*dec(".18")) + dec("32")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_MPPT_TEMPERATURE:
# Result is temperature in degrees Fahrenheit.
class power_MPPT_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 10
		self.upper_bound = 100
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = ((dec(rawdata)-dec("2731.6"))*dec(".18")) + dec("32")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_5C_VOLTAGE:
# Result is in volts.
class power_5C_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 4.7
		self.upper_bound = 5.1
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = dec(rawdata)/dec("500")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_5DAQ_VOLTAGE:
# Result is in volts.
class power_5DAQ_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 4.7
		self.upper_bound = 5.1
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = dec(rawdata)/dec("500")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_5DAQ_CURRENT:
# Result is in mA.
class power_5DAQ_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 30
		self.upper_bound = 1500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)/dec("6")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_VTOP_VOLTAGE:
# Result is in volts.
class power_VTOP_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 8
		self.upper_bound = 15
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (dec(rawdata)/1000)*dec("5.02")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_VTOP_CURRENT:
# Result is in mA.
class power_VTOP_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 400
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)/dec("6")
		return converted


#-------------------------------------------------------------------------------------------------------------------
#													POWER_VAUX_VOLTAGE:
# Result is in volts.
class power_VAUX_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 8
		self.upper_bound = 15
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (dec(rawdata)/1000)*dec("5.02")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_VAUX_CURRENT:
# Result is in volts.
class power_VAUX_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 400
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = dec(rawdata)/dec("6")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_DAQ_INPUT_CURRENT:
# Result is in mA.
class power_DAQ_input_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 500
		self.upper_bound = 1500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)/dec("2")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_BATTERY_TEMPERATURE_B:
# Result is in degrees Fahrenheit.
class power_battery_temperature_B(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 50
		self.upper_bound = 100
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = ((((dec(rawdata)/1024)*5)-dec("2.7316"))*180)+32
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_BOX_TEMPERATURE:
# Result is in degrees Fahrenheit.
class power_box_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 100
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = ((((dec(rawdata)/1024)*5)-dec("2.7316"))*180)+32
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_HEATER_CURRENT_B:
# Result is in mA.
class power_heater_current_B(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 700
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/6)*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_FAN_CURRENT_B:
# Result is in mA.
class power_fan_current_B(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 50
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/60)*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_STATUS
# the first bit of the power_status byte. 1 => fan is on
class power_status(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.dec_places_round = "N/A"
		self.raw_label = "power_status"

	def process(self, rawdata):
		binary = bin(int(rawdata))[2:].zfill(2)
		binarylength = len(binary)
		bit0 = int(binary[binarylength-1])
		bit1 = int(binary[binarylength-2])
		converted = ""
		if ((bit0) and (bit1)):
			converted += "heater on and fan on"
		if ((not bit0) and (bit1)):
			converted += "heater on and fan off"
		if ((bit0) and (not bit1)):
			converted += "fan on and heater off"
		if ((not bit0) and (not bit1)):
			converted += "fan off and heater off"
		return converted 

#-------------------------------------------------------------------------------------------------------------------
#													POWER_ENCLOSURE_HUMIDITY
# Result is percent humidity.
class power_enclosure_humidity(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 15
		self.upper_bound = 40
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_FAULT_STATUS
# fault.0=top fault, .1=daq box fault, .2=aux fault, .3=20WB in circuit
class power_fault_status(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.dec_places_round = "N/A"

	def process(self, rawdata):
		binary = bin(int(rawdata))[2:].zfill(4)
		binarylength = len(binary)
		bit0 = int(binary[binarylength-1])
		bit1 = int(binary[binarylength-2])
		bit2 = int(binary[binarylength-3])
		bit3 = int(binary[binarylength-4])
		converted = ""
		if bit0:
			converted += "top fault, "
		if bit1:
			converted += "DAQ box fault, "
		if bit2:
			converted += "AUX fault, "
		if bit3:
			converted += "20WB in circuit"
		converted = converted.rstrip(", ")
		if converted == "":
			converted = "OK"
			self.status_error = False
		elif not self.status_error:
			errors.error("power_fault_status reported " + converted)
			self.status_error = True
		return converted

#===================================================================================================================
#													SOIL SENSORS BLOCK
#===================================================================================================================
#
#-------------------------------------------------------------------------------------------------------------------
#													SOIL_TEMP_1_BELOW
# Result is in Fahrenheit
class soil_temp_1_below(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = ((dec(rawdata)/524288)*dec("4.096"))/10
		r = (20000*v)/(dec("4.096")-v)
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2)) + ((dec("1.0241")*dec(pow(10,-6)))*(r**3))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_TEMP_2_BELOW
# Result is in Fahrenheit
class soil_temp_2_below(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = ((dec(rawdata)/524288)*dec("4.096"))/10
		r = (20000*v)/(dec("4.096")-v)
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2)) + ((dec("1.0241")*dec(pow(10,-6)))*(r**3))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_TEMP_3_BELOW
# Result is in Fahrenheit
class soil_temp_3_below(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = ((dec(rawdata)/524288)*dec("4.096"))/10
		r = (20000*v)/(dec("4.096")-v)
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2)) + ((dec("1.0241")*dec(pow(10,-6)))*(r**3))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_TEMP_4_BELOW
# Result is in Fahrenheit
class soil_temp_4_below(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = ((dec(rawdata)/524288)*dec("4.096"))/10
		r = (20000*v)/(dec("4.096")-v)
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2)) + ((dec("1.0241")*dec(pow(10,-6)))*(r**3))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_TEMP_5_BELOW
# Result is in Fahrenheit
class soil_temp_5_below(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = ((dec(rawdata)/524288)*dec("4.096"))/10
		r = (20000*v)/(dec("4.096")-v)
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2)) + ((dec("1.0241")*dec(pow(10,-6)))*(r**3))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_TEMP_6_BELOW
# Result is in Fahrenheit
class soil_temp_6_below(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = ((dec(rawdata)/524288)*dec("4.096"))/10
		r = (20000*v)/(dec("4.096")-v)
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2)) + ((dec("1.0241")*dec(pow(10,-6)))*(r**3))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_TEMP_7_BELOW
# Result is in Fahrenheit
class soil_temp_7_below(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = ((dec(rawdata)/524288)*dec("4.096"))/10
		r = (20000*v)/(dec("4.096")-v)
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2)) + ((dec("1.0241")*dec(pow(10,-6)))*(r**3))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_TEMP_8_BELOW
# Result is in Fahrenheit
class soil_temp_8_below(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = ((dec(rawdata)/524288)*dec("4.096"))/10
		r = (20000*v)/(dec("4.096")-v)
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2)) + ((dec("1.0241")*dec(pow(10,-6)))*(r**3))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_TEMP_10_BELOW
# Result is in Fahrenheit
class soil_temp_10_below(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = ((dec(rawdata)/524288)*dec("4.096"))/10
		r = (20000*v)/(dec("4.096")-v)
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2)) + ((dec("1.0241")*dec(pow(10,-6)))*(r**3))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_TEMP_12_BELOW
# Result is in Fahrenheit
class soil_temp_12_below(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = ((dec(rawdata)/524288)*dec("4.096"))/10
		r = (20000*v)/(dec("4.096")-v)
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2)) + ((dec("1.0241")*dec(pow(10,-6)))*(r**3))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_TEMP_20_BELOW
# Result is in Fahrenheit
class soil_temp_20_below(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = ((dec(rawdata)/524288)*dec("4.096"))/10
		r = (20000*v)/(dec("4.096")-v)
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2)) + ((dec("1.0241")*dec(pow(10,-6)))*(r**3))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_TEMP_30_BELOW
# Result is in Fahrenheit
class soil_temp_30_below(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = ((dec(rawdata)/524288)*dec("4.096"))/10
		r = (20000*v)/(dec("4.096")-v)
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2)) + ((dec("1.0241")*dec(pow(10,-6)))*(r**3))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_TEMP_40_BELOW
# Result is in Fahrenheit
class soil_temp_40_below(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = ((dec(rawdata)/524288)*dec("4.096"))/10
		r = (20000*v)/(dec("4.096")-v)
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2)) + ((dec("1.0241")*dec(pow(10,-6)))*(r**3))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_TEMP_48_BELOW
# Result is in Fahrenheit
class soil_temp_48_below(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = ((dec(rawdata)/524288)*dec("4.096"))/10
		r = (20000*v)/(dec("4.096")-v)
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2)) + ((dec("1.0241")*dec(pow(10,-6)))*(r**3))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_MOIST_B2
# Result is in volumetric water content
class soil_moist_b2(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 50
		self.dec_places_round = 2

	def process(self, rawdata):
		v = dec(rawdata)/1000
		if ((v>dec("0")) and (v<=dec("1.1"))):
			converted = (10*v)-1
		elif ((v>dec("1.1")) and (v<=dec("1.3"))):
			converted = (25*v) - dec("17.5")
		elif ((v>dec("1.3")) and (v<=dec("1.82"))):
			converted = (dec("48.08")*v) - dec("47.5")
		elif((v>dec("1.82")) and (v<=dec("2.2"))):
			converted = (dec("26.32")*v) - dec("7.89")
		else:
			converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_MOIST_B4
# Result is in volumetric water content
class soil_moist_b4(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 50
		self.dec_places_round = 2

	def process(self, rawdata):
		v = dec(rawdata)/1000
		if ((v>dec("0")) and (v<=dec("1.1"))):
			converted = (10*v)-1
		elif ((v>dec("1.1")) and (v<=dec("1.3"))):
			converted = (25*v) - dec("17.5")
		elif ((v>dec("1.3")) and (v<=dec("1.82"))):
			converted = (dec("48.08")*v) - dec("47.5")
		elif((v>dec("1.82")) and (v<=dec("2.2"))):
			converted = (dec("26.32")*v) - dec("7.89")
		else:
			converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_MOIST_B6
# Result is in volumetric water content
class soil_moist_b6(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 50
		self.dec_places_round = 2

	def process(self, rawdata):
		v = dec(rawdata)/1000
		if ((v>dec("0")) and (v<=dec("1.1"))):
			converted = (10*v)-1
		elif ((v>dec("1.1")) and (v<=dec("1.3"))):
			converted = (25*v) - dec("17.5")
		elif ((v>dec("1.3")) and (v<=dec("1.82"))):
			converted = (dec("48.08")*v) - dec("47.5")
		elif((v>dec("1.82")) and (v<=dec("2.2"))):
			converted = (dec("26.32")*v) - dec("7.89")
		else:
			converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_MOIST_B8
# Result is in volumetric water content
class soil_moist_b8(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 50
		self.dec_places_round = 2

	def process(self, rawdata):
		v = dec(rawdata)/1000
		if ((v>dec("0")) and (v<=dec("1.1"))):
			converted = (10*v)-1
		elif ((v>dec("1.1")) and (v<=dec("1.3"))):
			converted = (25*v) - dec("17.5")
		elif ((v>dec("1.3")) and (v<=dec("1.82"))):
			converted = (dec("48.08")*v) - dec("47.5")
		elif((v>dec("1.82")) and (v<=dec("2.2"))):
			converted = (dec("26.32")*v) - dec("7.89")
		else:
			converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_MOIST_B10
# Result is in volumetric water content
class soil_moist_b10(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 50
		self.dec_places_round = 2

	def process(self, rawdata):
		v = dec(rawdata)/1000
		if ((v>dec("0")) and (v<=dec("1.1"))):
			converted = (10*v)-1
		elif ((v>dec("1.1")) and (v<=dec("1.3"))):
			converted = (25*v) - dec("17.5")
		elif ((v>dec("1.3")) and (v<=dec("1.82"))):
			converted = (dec("48.08")*v) - dec("47.5")
		elif((v>dec("1.82")) and (v<=dec("2.2"))):
			converted = (dec("26.32")*v) - dec("7.89")
		else:
			converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_MOIST_B15
# Result is in volumetric water content
class soil_moist_b15(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 50
		self.dec_places_round = 2

	def process(self, rawdata):
		v = dec(rawdata)/1000
		if ((v>dec("0")) and (v<=dec("1.1"))):
			converted = (10*v)-1
		elif ((v>dec("1.1")) and (v<=dec("1.3"))):
			converted = (25*v) - dec("17.5")
		elif ((v>dec("1.3")) and (v<=dec("1.82"))):
			converted = (dec("48.08")*v) - dec("47.5")
		elif((v>dec("1.82")) and (v<=dec("2.2"))):
			converted = (dec("26.32")*v) - dec("7.89")
		else:
			converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_MOIST_B20
# Result is in volumetric water content
class soil_moist_b20(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 50
		self.dec_places_round = 2

	def process(self, rawdata):
		v = dec(rawdata)/1000
		if ((v>dec("0")) and (v<=dec("1.1"))):
			converted = (10*v)-1
		elif ((v>dec("1.1")) and (v<=dec("1.3"))):
			converted = (25*v) - dec("17.5")
		elif ((v>dec("1.3")) and (v<=dec("1.82"))):
			converted = (dec("48.08")*v) - dec("47.5")
		elif((v>dec("1.82")) and (v<=dec("2.2"))):
			converted = (dec("26.32")*v) - dec("7.89")
		else:
			converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_MOIST_B40
# Result is in volumetric water content
class soil_moist_b40(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 50
		self.dec_places_round = 2

	def process(self, rawdata):
		v = dec(rawdata)/1000
		if ((v>dec("0")) and (v<=dec("1.1"))):
			converted = (10*v)-1
		elif ((v>dec("1.1")) and (v<=dec("1.3"))):
			converted = (25*v) - dec("17.5")
		elif ((v>dec("1.3")) and (v<=dec("1.82"))):
			converted = (dec("48.08")*v) - dec("47.5")
		elif((v>dec("1.82")) and (v<=dec("2.2"))):
			converted = (dec("26.32")*v) - dec("7.89")
		else:
			converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TEMP_1_ABOVE
# Result is in Fahrenheit
class temp_1_above(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = (dec(rawdata)/131072)*dec("4.096")
		r = (20000*v)/(dec("4.096")-v)
		a = dec("0.001125308852122")
		b = dec("0.000234711863267")
		c = dec("0.000000085663516")
		t = 1/(a + (b*(r.ln())) + (c*((r.ln())**3)))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TEMP_2_ABOVE
# Result is in Fahrenheit
class temp_2_above(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = (dec(rawdata)/131072)*dec("4.096")
		r = (20000*v)/(dec("4.096")-v)
		a = dec("0.001125308852122")
		b = dec("0.000234711863267")
		c = dec("0.000000085663516")
		t = 1/(a + (b*(r.ln())) + (c*((r.ln())**3)))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TEMP_3_ABOVE
# Result is in Fahrenheit
class temp_3_above(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = (dec(rawdata)/131072)*dec("4.096")
		r = (20000*v)/(dec("4.096")-v)
		a = dec("0.001125308852122")
		b = dec("0.000234711863267")
		c = dec("0.000000085663516")
		t = 1/(a + (b*(r.ln())) + (c*((r.ln())**3)))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TEMP_4_ABOVE
# Result is in Fahrenheit
class temp_4_above(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = (dec(rawdata)/131072)*dec("4.096")
		r = (20000*v)/(dec("4.096")-v)
		a = dec("0.001125308852122")
		b = dec("0.000234711863267")
		c = dec("0.000000085663516")
		t = 1/(a + (b*(r.ln())) + (c*((r.ln())**3)))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TEMP_5_ABOVE
# Result is in Fahrenheit
class temp_5_above(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = (dec(rawdata)/131072)*dec("4.096")
		r = (20000*v)/(dec("4.096")-v)
		a = dec("0.001125308852122")
		b = dec("0.000234711863267")
		c = dec("0.000000085663516")
		t = 1/(a + (b*(r.ln())) + (c*((r.ln())**3)))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TEMP_7_ABOVE
# Result is in Fahrenheit
class temp_7_above(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = (dec(rawdata)/131072)*dec("4.096")
		r = (20000*v)/(dec("4.096")-v)
		a = dec("0.001125308852122")
		b = dec("0.000234711863267")
		c = dec("0.000000085663516")
		t = 1/(a + (b*(r.ln())) + (c*((r.ln())**3)))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TEMP_9_ABOVE
# Result is in Fahrenheit
class temp_9_above(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = (dec(rawdata)/131072)*dec("4.096")
		r = (20000*v)/(dec("4.096")-v)
		a = dec("0.001125308852122")
		b = dec("0.000234711863267")
		c = dec("0.000000085663516")
		t = 1/(a + (b*(r.ln())) + (c*((r.ln())**3)))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TEMP_11_ABOVE
# Result is in Fahrenheit
class temp_11_above(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = (dec(rawdata)/131072)*dec("4.096")
		r = (20000*v)/(dec("4.096")-v)
		a = dec("0.001125308852122")
		b = dec("0.000234711863267")
		c = dec("0.000000085663516")
		t = 1/(a + (b*(r.ln())) + (c*((r.ln())**3)))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TEMP_13_ABOVE
# Result is in Fahrenheit
class temp_13_above(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = (dec(rawdata)/131072)*dec("4.096")
		r = (20000*v)/(dec("4.096")-v)
		a = dec("0.001125308852122")
		b = dec("0.000234711863267")
		c = dec("0.000000085663516")
		t = 1/(a + (b*(r.ln())) + (c*((r.ln())**3)))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TEMP_15_ABOVE
# Result is in Fahrenheit
class temp_15_above(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -30
		self.upper_bound = 120
		self.dec_places_round = 3

	def process(self, rawdata):
		v = (dec(rawdata)/131072)*dec("4.096")
		r = (20000*v)/(dec("4.096")-v)
		a = dec("0.001125308852122")
		b = dec("0.000234711863267")
		c = dec("0.000000085663516")
		t = 1/(a + (b*(r.ln())) + (c*((r.ln())**3)))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_FLUX
# Result is in watts per meter squared
class soil_flux(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0.15
		self.upper_bound = 0.85
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)/262144)*dec("4.096"))-dec("0.5026")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_ELECTRONICS_TEMP
# Result is in degrees F
class soil_electronics_temp(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 20
		self.upper_bound = 100
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = ((((dec(rawdata)/1024)*5)-dec("2.7316"))*180)+32
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_ELECTRONICS_VREF
# Result is in volts (may have to add some correction for a more accurate value)
class soil_electronics_Vref(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 4.08
		self.upper_bound = 4.1
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = (dec(rawdata)/1024)*5
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOIL_SPARE
# For future use
class soil_spare(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													OLD_WIND_CHILL
class old_wind_chill(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.dec_places_round = 2
		self.raw_label = "N/A"
		self.lower_bound = -120
		self.upper_bound = 120

	def process(self, rawdata): 
		windspeed = DataConverter.outputter.get_converted("vortex_avg_speed")
		temp = DataConverter.outputter.get_converted("Temperature_Precon")
		if windspeed == Config.ERROR_VAL or temp == Config.ERROR_VAL:
			raise DataMissingError("Lack necessary data to perform conversion.")
		converted = dec("91.4") - (dec("0.474677") - dec("0.020425")*dec(str(windspeed)) + dec("0.303107")*dec(str(sqrt(float(windspeed)))))*(dec("91.4") - dec(str(temp)))
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													NEW_WIND_CHILL
class new_wind_chill(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.dec_places_round = 2
		self.raw_label = "N/A"
		self.lower_bound = -120
		self.upper_bound = 120
		

	def process(self, rawdata): 
		windspeed = DataConverter.outputter.get_converted("vortex_avg_speed")
		temp = DataConverter.outputter.get_converted("Temperature_Precon")
		if windspeed == Config.ERROR_VAL or temp == Config.ERROR_VAL:
			raise DataMissingError("Lack necessary data to perform conversion.")
		converted = dec("35.74") + dec("0.6215")*dec(str(temp)) - dec("35.75")*dec(str(pow(float(temp), 0.16))) + dec("0.4275")*dec(str(temp))*dec(str(pow(float(temp), 0.16)))
		return converted

#===================================================================================================================
#...................................................................................................................
#...................................................................................................................
#...................................................GROUP 1.........................................................
#...................................................................................................................
#...................................................................................................................
#===================================================================================================================
#
#===================================================================================================================
#													DAQ MULTIPLEXER
#===================================================================================================================
#
#-------------------------------------------------------------------------------------------------------------------
#													MUX_CURRENT
class mux_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 12
		self.upper_bound = 490
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/6)*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													MUX_TEMPERATURE
class mux_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 2350
		self.upper_bound = 3175
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = ((((dec(rawdata)/1024)*5)-dec("2.73"))*180)+32
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													PEET_WIND_RATE
# Needs formula
class Peet_wind_rate(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													PEET_WIND_MUTL
class Peet_wind_multl(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													PEET_WINDLO
class Peet_windlo(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													PEET_WIND_MULTH
class Peet_wind_multh(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													PEET_WINDHI
class Peet_windhi(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													PEET_VDUCE
class Peet_vduce(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													PEET_WIND_SPEED
class Peet_wind_speed(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.raw_label = "N/A"
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													PEET_WINDDIR
class Peet_winddir(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													PEET_WIND_DIRECTION
class Peet_wind_direction(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.raw_label = "N/A"
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													INSPEED_WIND_DIRECTION
class Inspeed_wind_direction(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = ((dec(rawdata)-3277)/58982)*360
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													HYDREON_CURRENT
class Hydreon_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/30)*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													HYDREON_TEMPERATURE
class Hydreon_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 2350
		self.upper_bound = 3175
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = ((((dec(rawdata)/1024)*5)-dec("2.73"))*180)+32
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													HYDREON_RANGE_SETTING
class Hydreon_range_setting(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 0

	def process(self, rawdata):
		if dec(rawdata) == 0:
			converted = dec("0.01")
		elif dec(rawdata) == 2:
			converted = dec("0.001")
		elif dec(rawdata) == 4:
			converted = dec("0.0001")
		else:
			converted = dec("0.0") # CHANGE THIS (?)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													HYDREON_LOW_SENSE
class Hydreon_low_sense(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = "FIX"
		self.dec_places_round = "FIX"

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.01")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													HYDREON_MEDIUM_SENSE
class Hydreon_medium_sense(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = "FIX"
		self.dec_places_round = "FIX"

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.001")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													HYDREON_HIGH_SENSE
class Hydreon_high_sense(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = "FIX"
		self.dec_places_round = "FIX"

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.0001")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													HYDREON_RAIN_AMOUNT
class Hydreon_rain_amount(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.raw_label = "N/A"
		self.lower_bound = 0
		self.upper_bound = "FIX"
		self.dec_places_round = "FIX"

	def process(self, rawdata):
		rangesetting = DataConverter.reader.get("Hydreon_range_setting")
		if (rangesetting == 0):
			converted = DataConverter.reader.get("Hydreon_low_sense")
		if (rangesetting == 1):
			converted = DataConverter.reader.get("Hydreon_medium_sense")
		if (rangesetting == 4):
			converted = DataConverter.reader.get("Hydreon_high_sense")
		else:
			converted = converted = DataConverter.reader.get("Hydreon_low_sense")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SKY_SENSOR_CURRENT
class sky_sensor_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/60)*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SKY_SWIPER_CW_CURRENT
class sky_swiper_CW_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/60)*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SKY_SWIPER_CCW_CURRENT
class sky_swiper_CCW_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/60)*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SKY_DARK_READING
class sky_dark_reading(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = (((dec(rawdata)/65536)*5)*1000)/dec("3.399")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SKY_BRIGHT_READING
class sky_bright_reading(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = ((dec(rawdata)/65536)*5)/dec("0.003399")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SKY_IR_TEMPERATURE
class sky_IR_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (((dec(rawdata)/50)-dec("2.7315"))*180)+32
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SKY_SENSOR_STATUS
class sky_sensor_status(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = "FIX"

	def process(self, rawdata):
		binary = bin(int(rawdata))[2:].zfill(8)
		binarylength = len(binary)
		bit0 = int(binary[binarylength-1])
		bit1 = int(binary[binarylength-2])
		bit7 = int(binary[binarylength-8])
		converted = ""
		if (not bit0):
			converted += "home loop not overrun, "
		if bit0:
			converted += "error for >520 pulses, "
		if bit1:
			converted += "motor is running, "
		if bit7:
			converted += "swipe stop bit is set, "
		converted = converted.rstrip(', ')
		if converted == "":
			converted = "OK"
			self.status_error = False
		elif not self.status_error:
			errors.error("Sky sensor status reported " + converted)
			self.status_error = True
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SKY_HALL_SENSOR
class sky_Hall_sensor(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = (dec(rawdata)/1024)*5
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X40_READING
class sway_X40_reading(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.001")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X1_READING
class sway_X1_reading(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.001")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y1_READING
class sway_Y1_reading(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.001")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y40_READING
class sway_Y40_reading(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.001")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SWAY_SENSOR_TEMPERATURE
class sway_sensor_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)*dec("0.001"))-dec("2.7315"))*180)+32
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SWAY_SENSOR_VSS
class sway_sensor_Vss(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = (dec(rawdata)*dec("0.001"))*2
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SWAY-Z_OFFSET
class sway_Z_offset(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.001")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Z50_READING
class sway_Z50_reading(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.001")
		return converted

#===================================================================================================================
#													LIGHTNING
#===================================================================================================================
#
#-------------------------------------------------------------------------------------------------------------------
#													LIGHTNING_CURRENT
class lightning_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/60)*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													LIGHTNING_UV_COUNT
class lightning_UV_count(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													LIGHTNING_HIGH_VOLTAGE
class lightning_high_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = ((dec(rawdata)/1024)*5)*214
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													LIGHTNING_3001_LUX
class lightning_3001_lux(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 0

	def process(self, rawdata):
		upper = hex(int(rawdata))[2:3]
		lower = hex(int(rawdata))[3:6]
		e = int(upper, base=16)
		r = int(lower, base=16)
		converted = (dec("0.01")*(2**e))*r
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													LIGHTNING_SKYSCAN_CURRENT
class lightning_Skyscan_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/30)*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													LIGHTNING_SKYSCAN_LEDS
class lightning_Skyscan_LEDs(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = "FIX"

	def process(self, rawdata):
		binary = bin(int(rawdata))[2:].zfill(8)
		binarylength = len(binary)
		bit0 = int(binary[binarylength-1])
		bit1 = int(binary[binarylength-2])
		bit2 = int(binary[binarylength-3])
		bit3 = int(binary[binarylength-4])
		bit4 = int(binary[binarylength-5])
		bit5 = int(binary[binarylength-6])
		converted = ""
		if bit0:
			converted += "severe storm, "
		if bit1: 
			converted += "3 miles, "
		if bit2:
			converted += "8 miles, "
		if bit3:
			converted += "20 miles, "
		if bit4:
			converted += "40 miles, "
		if bit5:
			converted += "power LED, "
		converted = converted.rstrip(', ')
		if converted == "":
			converted = "OK"
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													LIGHTNING_SKYSCAN_FLASH_TIME
class lightning_Skyscan_flash_time(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													LIGHTNING_SKYSCAN_ALARMS
class lightning_Skyscan_alarms(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = "FIX"

	def process(self, rawdata):
		binary = bin(int(rawdata))[2:].zfill(8)
		binarylength = len(binary)
		bit0 = int(binary[binarylength-1])
		bit1 = int(binary[binarylength-2])
		bit2 = int(binary[binarylength-3])
		bit3 = int(binary[binarylength-4])
		bit4 = int(binary[binarylength-5])
		bit5 = int(binary[binarylength-6])
		bit6 = int(binary[binarylength-7])
		bit7 = int(binary[binarylength-8])
		converted = ""
		if bit0:
			converted += "severe, "
		if bit1: 
			converted += "0-3, "
		if bit2:
			converted += "3-8, "
		if bit3:
			converted += "8-20, "
		if bit4:
			converted += "20-40, "
		if bit5:
			converted += "na, "
		if bit6:
			converted += "false alarm, "
		if bit7:
			converted += "alarm, "
		converted = converted.rstrip(', ')
		if converted == "":
			converted = "OK"
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													LIGHTNING_OPT101_BASELINE
class lightning_OPT101_baseline(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.001")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													LIGHTNING_OPT101_NORTH
class lightning_OPT101_north(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.001")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													LIGHTNING_OPT101_SOUTH
class lightning_OPT101_south(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.001")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													LIGHTNING_OPT101_EAST
class lightning_OPT101_east(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.001")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													LIGHTNING_OPT101_WEST
class lightning_OPT101_west(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.001")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													LIGHTNING_OPT101_ZENITH
class lightning_OPT101_zenith(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.001")
		return converted

#===================================================================================================================
#													PIC CLUSTER
#===================================================================================================================
#
#-------------------------------------------------------------------------------------------------------------------
#													LIGHTNING_THUNDER
class lightning_thunder(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/1024
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													LIGHTNING_FLAG
class lightning_flag(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = "FIX"

	def process(self, rawdata):
		binary = bin(int(rawdata))[2:].zfill(3)
		binarylength = len(binary)
		bit0 = int(binary[binarylength-1])
		bit1 = int(binary[binarylength-2])
		bit2 = int(binary[binarylength-3])
		converted = ""
		if bit0:
			converted += "gain at minimum, "
		if bit1: 
			converted += "gain at max, "
		if bit2:
			converted += "OPT101 gain within range, "
		converted = converted.rstrip(', ')
		if converted == "":
			converted = "OK"
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													LIGHTNING_UVA_UVB
class lightning_UVA_UVB(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-1)*dec("8.2")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													LIGHTNING_OPT_TEMPERATURE
class lightning_OPT_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)*dec("0.001"))-dec("2.7315"))*180)+32
		return converted

#===================================================================================================================
#													SOLAR DAQ
#===================================================================================================================
#
#-------------------------------------------------------------------------------------------------------------------
#													SOLAR_BOX_TEMPERATURE
class solar_box_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = ((((dec(rawdata)/65536)*10)-dec("2.7315"))*180)+32
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOLAR_PYRAN_COMBINED:
class solar_pyran_combined(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.raw_label = "N/A"
		self.lower_bound = 0
		self.upper_bound = 1200
		self.dec_places_round = 3

	def process(self, rawdata):
		upper = DataConverter.reader.get("solar_pyran_upper_byte")
		middle = DataConverter.reader.get("solar_pyran_middle_byte")
		lower = DataConverter.reader.get("solar_pyran_lower_byte")
		combined = int(upper + middle + lower, base = 16)
		converted = (((dec(combined)/16777216)*5)*5)*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOLAR_PAR_COMBINED:
class solar_par_combined(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.raw_label = "N/A"
		self.lower_bound = 0
		self.upper_bound = 2100
		self.dec_places_round = 3

	def process(self, rawdata):
		upper = DataConverter.reader.get("solar_par_upper_byte")
		middle = DataConverter.reader.get("solar_par_middle_byte")
		lower = DataConverter.reader.get("solar_par_lower_byte")
		combined = int(upper + middle + lower, base = 16)
		converted = (((dec(combined)/16777216)*5)*5)*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOLAR_UV_COMBINED:
class solar_UV_combined(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.raw_label = "N/A"
		self.lower_bound = 0
		self.upper_bound = 175
		self.dec_places_round = 3

	def process(self, rawdata):
		upper = DataConverter.reader.get("solar_UV_upper_byte")
		middle = DataConverter.reader.get("solar_UV_middle_byte")
		lower = DataConverter.reader.get("solar_UV_lower_byte")
		combined = int(upper + middle + lower, base = 16)
		converted = (((dec(combined)/16777216)*5)*dec("1.65"))*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOLAR_GOLD_GRID_EAST
class solar_gold_grid_east(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 4

	def process(self, rawdata):
		converted = (dec(rawdata)/65536)*5
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOLAR_GOLD_GRID_WEST
class solar_gold_grid_west(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 4

	def process(self, rawdata):
		converted = (dec(rawdata)/65536)*5
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOLAR_DECAGON_HORIZONTAL
class solar_Decagon_horizontal(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 4

	def process(self, rawdata):
		converted = (dec(rawdata)/65536)*5
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOLAR_DECAGON_TILTED
class solar_Decagon_tilted(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 4

	def process(self, rawdata):
		converted = (dec(rawdata)/65536)*5
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOLAR_FROST
class solar_frost(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		r = 24900*((5/((dec(rawdata)/65536)*5))-1)
		a = dec("1.1292418")*dec(pow(10,-3))
		b = dec("2.341077")*dec(pow(10,-4))
		c = dec("8.775468")*dec(pow(10,-8))
		converted = (1/(a+(b*(r.ln())) + (c*((r.ln())**3))))
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOLAR_BUD
class solar_bud(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		r = 24900*((5/((dec(rawdata)/65536)*5))-1)
		a = dec("1.1292418")*dec(pow(10,-3))
		b = dec("2.341077")*dec(pow(10,-4))
		c = dec("8.775468")*dec(pow(10,-8))
		converted = (1/(a+(b*(r.ln())) + (c*((r.ln())**3))))
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOLAR_GLOBE_COMBINED:
class solar_globe_combined(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.raw_label = "N/A"
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 4

	def process(self, rawdata):
		upper = DataConverter.reader.get("solar_globe_upper_byte")
		middle = DataConverter.reader.get("solar_globe_middle_byte")
		lower = DataConverter.reader.get("solar_globe_lower_byte")
		combined = int(upper + middle + lower, base = 16)
		r = (((dec(combined)/8388608)*dec("2.5"))/dec("0.0005"))/10
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2)) + ((dec("1.0241")*dec(pow(10,-6)))*(r**3))
		converted = (t*(dec(9/5))) - dec("459.67")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOLAR_CURRENT
class solar_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = (((dec(rawdata)/65536)*5)/30)*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SOLAR_VOLTAGE
class solar_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 4

	def process(self, rawdata):
		converted = ((dec(rawdata)/65536)*5)*10
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													SOLAR_IR_GROUND_TEMPERATURE
class solar_IR_ground_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = (((dec(rawdata)/50)-dec("2.7315"))*180)+32
		return converted

#===================================================================================================================
#													MET ONE ANEMOMETER
#===================================================================================================================
#
#-------------------------------------------------------------------------------------------------------------------
#													METONE_LED_CURRENT
class MetOne_LED_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 450
		self.upper_bound = 700
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/600)*1000
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													METONE_PULSEWIDTH
class MetOne_pulsewidth(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = "FIX"

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													METONE_TICKS_COUNT
class MetOne_ticks_count(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 1000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = (dec(rawdata)*dec("0.059307"))+dec("0.5982")
		return converted
		
#===================================================================================================================
#													POWER DISTR. AND FUSING
#===================================================================================================================
#
#-------------------------------------------------------------------------------------------------------------------
#													FUSES_ARBCAM_CURRENT
class fuses_Arbcam_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/6)*1000
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FUSES_ARBCAM_VOLTAGE
class fuses_Arbcam_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = ((dec(rawdata)/1024)*5)*4
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FUSES_5.6_VOLTAGE
class fuses_5V6_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)/1024)*5)*2
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FUSES_MUX_CURRENT
class fuses_mux_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/6)*1000
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FUSES_LIGHTNING_CURRENT
class fuses_lightning_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/6)*1000
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FUSES_SOLAR_DAQ_CURRENT
class fuses_solar_DAQ_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/60)*1000
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FUSES_FLUXGATE_CURRENT
class fuses_fluxgate_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/60)*1000
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FUSES_TRIAXIAL_CURRENT
class fuses_triaxial_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/60)*1000
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FUSES_FUTURE_CURRENT
class fuses_future_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/6)*1000
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FUSES_FLAG
class fuses_flag(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = "FIX"

	def process(self, rawdata):
		binary = bin(int(rawdata))[2:].zfill(7)
		binarylength = len(binary)
		bit0 = int(binary[binarylength-1])
		bit1 = int(binary[binarylength-2])
		bit2 = int(binary[binarylength-3])
		bit3 = int(binary[binarylength-4])
		bit4 = int(binary[binarylength-5])
		bit5 = int(binary[binarylength-6])
		bit6 = int(binary[binarylength-7])
		converted = ""
		if bit0:
			converted += "mux ovld, "
		if bit1: 
			converted += "lightning ovld, "
		if bit2:
			converted += "solar ovld, "
		if bit3:
			converted += "spare olvd, "
		if bit4:
			converted += "flux olvd, "
		if bit5:
			converted += "triax olvd, "
		if bit6:
			converted += "Arbcam overload, "
		converted = converted.rstrip(', ')
		if converted == "":
			converted = "OK"
			self.status_error = False
		elif not self.status_error:
			errors.error("Fuses flag reported " + converted)
			self.status_error = True
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FUSES_WARN
class fuses_warn(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = "FIX"

	def process(self, rawdata):
		binary = bin(int(rawdata))[2:].zfill(7)
		binarylength = len(binary)
		bit0 = int(binary[binarylength-1])
		bit1 = int(binary[binarylength-2])
		bit2 = int(binary[binarylength-3])
		bit3 = int(binary[binarylength-4])
		bit4 = int(binary[binarylength-5])
		bit5 = int(binary[binarylength-6])
		bit6 = int(binary[binarylength-7])
		converted = ""
		if bit0:
			converted += "mux warning, "
		if bit1: 
			converted += "lightning warning, "
		if bit2:
			converted += "solar warning, "
		if bit3:
			converted += "spare warning, "
		if bit4:
			converted += "flux warning, "
		if bit5:
			converted += "triax warning, "
		if bit6:
			converted += "Arbcam current high warning, "
		converted = converted.rstrip(', ')
		if converted == "":
			converted = "OK"
			self.status_error = False
		elif not self.status_error:
			errors.error("Fuses warn reported " + converted)
			self.status_error = True
		return converted
#-------------------------------------------------------------------------------------------------------------------
#													FUSES_GO_UP
class fuses_go_up(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = "FIX"

	def process(self, rawdata):
		binary = bin(int(rawdata))[2:].zfill(7)
		binarylength = len(binary)
		bit0 = int(binary[binarylength-1])
		bit1 = int(binary[binarylength-2])
		bit2 = int(binary[binarylength-3])
		bit3 = int(binary[binarylength-4])
		bit4 = int(binary[binarylength-5])
		bit5 = int(binary[binarylength-6])
		bit6 = int(binary[binarylength-7])
		converted = ""
		if bit0:
			converted += "mux rising, "
		if bit1: 
			converted += "lightning rising, "
		if bit2:
			converted += "solar rising, "
		if bit3:
			converted += "spare rising, "
		if bit4:
			converted += "flux rising, "
		if bit5:
			converted += "triax rising, "
		if bit6:
			converted += "Arbcam current above limit and rising, "
		converted = converted.rstrip(', ')
		if converted == "":
			converted = "OK"
			self.status_error = False
		elif not self.status_error:
			errors.error("Fuses go up reported " + converted)
			self.status_error = True
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FUSES_MONITOR
class fuses_monitor(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = "FIX"

	def process(self, rawdata):
		binary = bin(int(rawdata))[2:].zfill(7)
		binarylength = len(binary)
		bit0 = int(binary[binarylength-1])
		bit1 = int(binary[binarylength-2])
		bit2 = int(binary[binarylength-3])
		bit3 = int(binary[binarylength-4])
		bit4 = int(binary[binarylength-5])
		bit5 = int(binary[binarylength-6])
		bit6 = int(binary[binarylength-7])
		converted = ""
		if bit0:
			converted += "mux ovld, "
		if bit1: 
			converted += "lightning ovld, "
		if bit2:
			converted += "solar ovld, "
		if bit3:
			converted += "spare olvd, "
		if bit4:
			converted += "flux olvd, "
		if bit5:
			converted += "triax olvd, "
		if bit6:
			converted += "Arbcam overload, "
		converted = converted.rstrip(', ')
		if converted == "":
			converted = "OK"
			self.status_error = False
		elif not self.status_error:
			errors.error("Fuses monitor reported " + converted)
			self.status_error = True
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FUSES_ARBCAM_MODE
class fuses_Arbcam_mode(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = "FIX"

	def process(self, rawdata):
		binary = bin(int(rawdata))[2:].zfill(2)
		binarylength = len(binary)
		bit0 = int(binary[binarylength-1])
		bit1 = int(binary[binarylength-2])
		converted = ""
		if bit0:
			converted += "camera on with no heater, "
		if bit1: 
			converted += "camera on with heater, "
		converted = converted.rstrip(', ')
		if converted == "":
			converted = "OK"
			self.status_error = False
		elif not self.status_error:
			errors.error("Fuses arbcam mode reported " + converted)
			self.status_error = True
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FUSES_FAULT_STATUS
class fuses_fault_status(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = "FIX"

	def process(self, rawdata):
		binary = bin(int(rawdata))[2:].zfill(4)
		binarylength = len(binary)
		bit0 = int(binary[binarylength-1])
		bit1 = int(binary[binarylength-2])
		bit2 = int(binary[binarylength-3])
		bit3 = int(binary[binarylength-4])
		converted = ""
		if bit0:
			converted += "5.6 supply <5.4, "
		if bit1: 
			converted += "5.6 supply >5.8, "
		if bit2:
			converted += "Arbcam undervoltage, "
		if bit3:
			converted += "Arbcam overvoltage, "
		converted = converted.rstrip(', ')
		if converted == "":
			converted = "OK"
			self.status_error = False
		elif not self.status_error:
			errors.error("Fuses fault status reported " + converted)
			self.status_error = True
		return converted
		
#===================================================================================================================
#													POWER MONITORING
#===================================================================================================================
#
#-------------------------------------------------------------------------------------------------------------------
#													POWER_SOLAR_PANEL_CURRENT
class power_solar_panel_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)/1024)*5)/6)*1000
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													POWER_SOLAR_PANEL_VOLTAGE
class power_solar_panel_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (dec(rawdata)*dec("0.001"))*10
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													POWER_BATTERY_CURRENT
class pm_battery_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))/6)*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_BATTERY_VOLTAGE
class pm_battery_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (dec(rawdata)*dec("0.001"))*10
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													POWER_CURRENT_INTO_5V6
class power_current_into_5V6(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))/6)*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_VOLTAGE_INTO_5V6
class power_voltage_into_5V6(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (dec(rawdata)*dec("0.001"))*10
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													POWER_5V6_LOAD_CURRENT
class power_5V6_load_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))/6)*1000
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_5V6_LOAD_VOLTAGE
class power_5V6_load_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (dec(rawdata)*dec("0.001"))*2
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													POWER_BOX_TEMPERATURE
class pm_box_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)*dec("0.001"))-dec("2.7315"))*180)+32
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													POWER_ARBCAM_DCDC_INPUT_CURRENT
class power_Arbcam_dcdc_input_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))/6)*1000
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													POWER_ARBCAM_DCDC_INPUT_VOLTAGE
class power_Arbcam_dcdc_input_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (dec(rawdata)*dec("0.001"))*10
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													POWER_ARBCAM_CURRENT
class power_Arbcam_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))/6)*1000
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													POWER_ARBCAM_VOLTAGE
class power_Arbcam_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (dec(rawdata)*dec("0.001"))*4
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													POWER_BATTERY_TEMPERATURE
class power_battery_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = (((dec(rawdata)*dec("0.001"))-dec("2.7315"))*180)+32
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													POWER_128K_BATTERY_VOLTAGE
class power_128K_battery_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.001")
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													POWER_RTC_BATTERY_VOLTAGE
class power_RTC_battery_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.001")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													POWER_RTD_30FT_TEMPERATURE
class power_RTD_30ft_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 2

	def process(self, rawdata):
		r = ((dec(rawdata)/65536)*dec("4.096"))*1000
		t = dec("-247.29") + (dec("2.3992")*r) + (dec("0.00063962")*(r**2)) + ((dec("1.0241")*dec(pow(10,-6)))*(r**3))
		converted = (t*dec(9/5))-dec("459.67") 
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													POWER_HAIL_PEAK
class power_hail_peak(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = (dec(rawdata)/1024)*5
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													POWER_HAIL_AVERAGE
class power_hail_average(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = (dec(rawdata)/1024)*5
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													POWER_STATUS
class pm_status(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = "FIX"

	def process(self, rawdata):
		binary = bin(int(rawdata))[2:].zfill(8)
		binarylength = len(binary)
		bit4 = int(binary[binarylength-5])
		bit5 = int(binary[binarylength-6])
		bit6 = int(binary[binarylength-7])
		bit7 = int(binary[binarylength-8])
		converted = ""
		if bit4:
			converted += "latched off mode, "
		if bit5: 
			converted += "V>5.9v, "
		if bit6:
			converted += "5.68<V<5.9v, "
		if bit7:
			converted += "voltage within limits, "
		converted = converted.rstrip(', ')
		if converted == "":
			converted = "OK"
			self.status_error = False
		elif not self.status_error:
			errors.error("Power status reported " + converted)
			self.status_error = True
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													POWER_OVP_CYCLES
class power_OVP_cycles(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													POVER_OVP_VOLTAGE
class power_OVP_voltage(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = ((dec(rawdata)/1024)*5)*2
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													POWER_HAIL_SENSOR_TEMPERATURE
class power_hail_sensor_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 1

	def process(self, rawdata):
		converted = ((((dec(rawdata)/1024)*5)-dec("2.73"))*180)+32
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													POWER_HAIL_SENSOR_HITS
class power_hail_sensor_hits(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 0
		
	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													POWER_BOX_HUMIDITY
class power_box_humidity(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 15
		self.upper_bound = 40
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted

#===================================================================================================================
#...................................................................................................................
#...................................................................................................................
#...................................................GROUP 2.........................................................
#...................................................................................................................
#...................................................................................................................
#===================================================================================================================
#
#===================================================================================================================
#													SWAY SENSOR XY DATA
#===================================================================================================================
#				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X1
class sway_X1(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X2
class sway_X2(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X3
class sway_X3(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X4
class sway_X4(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X5
class sway_X5(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X6
class sway_X6(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X7
class sway_X7(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X8
class sway_X8(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X9
class sway_X9(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X10
class sway_X10(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X11
class sway_X11(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X12
class sway_X12(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X13
class sway_X13(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X14
class sway_X14(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X15
class sway_X15(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X16
class sway_X16(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X17
class sway_X17(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X18
class sway_X18(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X19
class sway_X19(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X20
class sway_X20(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X21
class sway_X21(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X22
class sway_X22(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X23
class sway_X23(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X24
class sway_X24(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X25
class sway_X25(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X26
class sway_X26(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X27
class sway_X27(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X28
class sway_X28(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X29
class sway_X29(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X30
class sway_X30(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X31
class sway_X31(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X32
class sway_X32(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X33
class sway_X33(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X34
class sway_X34(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3
		
	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X35
class sway_X35(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X36
class sway_X36(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X37
class sway_X37(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X38
class sway_X38(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X39
class sway_X39(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_X40
class sway_X40(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y1
class sway_Y1(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y2
class sway_Y2(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y3
class sway_Y3(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y4
class sway_Y4(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y5
class sway_Y5(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y6
class sway_Y6(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y7
class sway_Y7(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y8
class sway_Y8(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y9
class sway_Y9(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y10
class sway_Y10(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y11
class sway_Y11(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y12
class sway_Y12(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y13
class sway_Y13(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y14
class sway_Y14(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3
		
	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y15
class sway_Y15(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y16
class sway_Y16(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y17
class sway_Y17(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y18
class sway_Y18(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y19
class sway_Y19(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y20
class sway_Y20(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y21
class sway_Y21(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y22
class sway_Y22(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y23
class sway_Y23(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y24
class sway_Y24(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y25
class sway_Y25(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y26
class sway_Y26(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y27
class sway_Y27(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y28
class sway_Y28(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y29
class sway_Y29(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y30
class sway_Y30(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y31
class sway_Y31(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y32
class sway_Y32(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y33
class sway_Y33(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y34
class sway_Y34(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3
		
	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y35
class sway_Y35(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y36
class sway_Y36(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y37
class sway_Y37(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y38
class sway_Y38(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y39
class sway_Y39(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													SWAY_Y40
class sway_Y40(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 980
		self.upper_bound = 2300
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = ((dec(rawdata)*dec("0.001"))-dec("1.65"))/dec("0.3")
		return converted
		
#===================================================================================================================
#...................................................................................................................
#...................................................................................................................
#...................................................GROUP 3.........................................................
#...................................................................................................................
#...................................................................................................................
#===================================================================================================================
#
#===================================================================================================================
#													FLUXGATE MAGNETOMETER
#===================================================================================================================
#				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_T1
class fluxgate_T1(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 14
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_X1
class fluxgate_X1(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Y1
class fluxgate_Y1(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Z1
class fluxgate_Z1(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_T2
class fluxgate_T2(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 14
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_X2
class fluxgate_X2(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Y2
class fluxgate_Y2(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Z2
class fluxgate_Z2(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_T3
class fluxgate_T3(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 14
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_X3
class fluxgate_X3(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Y3
class fluxgate_Y3(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Z3
class fluxgate_Z3(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_T4
class fluxgate_T4(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 14
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_X4
class fluxgate_X4(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Y4
class fluxgate_Y4(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Z4
class fluxgate_Z4(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_T5
class fluxgate_T5(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 14
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_X5
class fluxgate_X5(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Y5
class fluxgate_Y5(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Z5
class fluxgate_Z5(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_T6
class fluxgate_T6(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 14
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_X6
class fluxgate_X6(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Y6
class fluxgate_Y6(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Z6
class fluxgate_Z6(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_T7
class fluxgate_T7(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 14
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_X7
class fluxgate_X7(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Y7
class fluxgate_Y7(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Z7
class fluxgate_Z7(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_T8
class fluxgate_T8(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 14
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_X8
class fluxgate_X8(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Y8
class fluxgate_Y8(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Z8
class fluxgate_Z8(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_T9
class fluxgate_T9(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 14
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_X9
class fluxgate_X9(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Y9
class fluxgate_Y9(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Z9
class fluxgate_Z9(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_T10
class fluxgate_T10(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 14
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_X10
class fluxgate_X10(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Y10
class fluxgate_Y10(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Z10
class fluxgate_Z10(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_T11
class fluxgate_T11(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 14
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_X11
class fluxgate_X11(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Y11
class fluxgate_Y11(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Z11
class fluxgate_Z11(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_T12
class fluxgate_T12(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 14
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_X12
class fluxgate_X12(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Y12
class fluxgate_Y12(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Z12
class fluxgate_Z12(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_T13
class fluxgate_T13(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 14
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_X13
class fluxgate_X13(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Y13
class fluxgate_Y13(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Z13
class fluxgate_Z13(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_T14
class fluxgate_T14(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 14
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_X14
class fluxgate_X14(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Y14
class fluxgate_Y14(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_Z14
class fluxgate_Z14(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 1000
		self.upper_bound = 12500
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)*10
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_CURRENT
class fluxgate_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 125
		self.upper_bound = 980
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (((dec(rawdata)/dec("1024"))*dec("5"))/dec("6"))*dec("1000")
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_TEMPERATURE
class fluxgate_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 2350
		self.upper_bound = 3175
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = ((((dec(rawdata)/dec("1024"))*dec("5"))-dec("2.73"))*dec("180"))+dec("32")
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_XSET
class fluxgate_xset(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 4000
		self.dec_places_round = 4

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.001")
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_YSET
class fluxgate_yset(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 4000
		self.dec_places_round = 4

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.001")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_ZSET
class fluxgate_zset(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 4000
		self.dec_places_round = 4

	def process(self, rawdata):
		converted = dec(rawdata)*dec("0.001")
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													FLUXGATE_FLAG
class fluxgate_flag(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 3
		self.dec_places_round = "N/A"

	def process(self, rawdata):
		binary = bin(int(rawdata))[2:].zfill(5)
		binarylength = len(binary)
		bit5 = int(binary[binarylength-6])
		converted = ""
		if bit5: 
			converted += "sensor power on"
		else:
			converted += "sensor power off"
		converted = converted.rstrip(', ')
		if converted == "":
			converted = "OK"
			self.status_error = False
		elif not self.status_error:
			errors.error("Fluxgate Flag reported " + converted)
			self.status_error = True
		return converted

#===================================================================================================================
#...................................................................................................................
#...................................................................................................................
#...................................................GROUP 4.........................................................
#...................................................................................................................
#...................................................................................................................
#===================================================================================================================
#
#===================================================================================================================
#													TRIAXIAL MAGNETOMETER
#===================================================================================================================
#				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T1
class triaxial_T1(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X1
class triaxial_X1(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y1
class triaxial_Y1(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z1
class triaxial_Z1(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T2
class triaxial_T2(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X2
class triaxial_X2(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y2
class triaxial_Y2(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z2
class triaxial_Z2(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T3
class triaxial_T3(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X3
class triaxial_X3(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y3
class triaxial_Y3(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z3
class triaxial_Z3(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T4
class triaxial_T4(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X4
class triaxial_X4(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y4
class triaxial_Y4(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z4
class triaxial_Z4(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T5
class triaxial_T5(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X5
class triaxial_X5(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y5
class triaxial_Y5(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z5
class triaxial_Z5(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T6
class triaxial_T6(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X6
class triaxial_X6(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y6
class triaxial_Y6(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z6
class triaxial_Z6(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T7
class triaxial_T7(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X7
class triaxial_X7(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y7
class triaxial_Y7(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z7
class triaxial_Z7(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T8
class triaxial_T8(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X8
class triaxial_X8(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y8
class triaxial_Y8(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z8
class triaxial_Z8(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T9
class triaxial_T9(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X9
class triaxial_X9(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y9
class triaxial_Y9(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z9
class triaxial_Z9(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T10
class triaxial_T10(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X10
class triaxial_X10(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y10
class triaxial_Y10(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z10
class triaxial_Z10(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T11
class triaxial_T11(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X11
class triaxial_X11(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y11
class triaxial_Y11(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z11
class triaxial_Z11(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T12
class triaxial_T12(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X12
class triaxial_X12(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y12
class triaxial_Y12(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z12
class triaxial_Z12(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T13
class triaxial_T13(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X13
class triaxial_X13(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y13
class triaxial_Y13(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z13
class triaxial_Z13(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T14
class triaxial_T14(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X14
class triaxial_X14(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y14
class triaxial_Y14(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z14
class triaxial_Z14(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T15
class triaxial_T15(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X15
class triaxial_X15(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y15
class triaxial_Y15(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z15
class triaxial_Z15(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T16
class triaxial_T16(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X16
class triaxial_X16(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y16
class triaxial_Y16(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z16
class triaxial_Z16(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T17
class triaxial_T17(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X17
class triaxial_X17(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y17
class triaxial_Y17(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z17
class triaxial_Z17(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted

#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T18
class triaxial_T18(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X18
class triaxial_X18(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y18
class triaxial_Y18(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z18
class triaxial_Z18(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T19
class triaxial_T19(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X19
class triaxial_X19(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y19
class triaxial_Y19(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z19
class triaxial_Z19(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_T20
class triaxial_T20(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 20
		self.dec_places_round = 0

	def process(self, rawdata):
		converted = dec(rawdata)
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_X20
class triaxial_X20(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Y20
class triaxial_Y20(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_Z20
class triaxial_Z20(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 0
		self.upper_bound = 32000
		self.dec_places_round = 3

	def process(self, rawdata):
		converted = dec(rawdata)/dec("62.48")
		return converted
		
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_CURRENT
class triaxial_current(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = "FIX"
		self.upper_bound = "FIX"
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = (((dec(rawdata)/dec("1024"))*dec("5"))/dec("300"))*dec("1000")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_VOLTS
class triaxial_volts(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = 4.8
		self.upper_bound = 5.1
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = ((dec(rawdata)/dec("1024"))*dec("5"))*dec("2")
		return converted
				
#-------------------------------------------------------------------------------------------------------------------
#													TRIAXIAL_TEMPERATURE
class triaxial_temperature(DataConverter):
	def __init__(self):
		DataConverter.__init__(self)
		self.lower_bound = -40
		self.upper_bound = 110
		self.dec_places_round = 2

	def process(self, rawdata):
		converted = ((((dec(rawdata)/dec("1024"))*dec("5"))-dec("2.73"))*dec("180"))+dec("32")
		return converted

#***************ADD NEW DATACONVERTERS TO CONVERT.PY WHEN DEFINED***************#
