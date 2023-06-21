# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import octoprint.plugin
import RPi.GPIO as GPIO
from flask import jsonify, request


class HeatBedSavetyPlugin(octoprint.plugin.StartupPlugin,
						  octoprint.plugin.ShutdownPlugin,
						  octoprint.plugin.EventHandlerPlugin,
						  octoprint.plugin.TemplatePlugin,
						  octoprint.plugin.SettingsPlugin,
						  octoprint.plugin.AssetPlugin,
						  octoprint.plugin.BlueprintPlugin):

	def __init__(self):
		self.i = 0
		self._gpioup = 0
		self._powerup = 0
		self._onevents = ["OPERATIONAL"]
		self._offevents = ["ERROR", "CLOSED_WITH_ERROR", ]


	def _initgpio(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(26, GPIO.OUT)
		self._gpioup = 1


	def readtemperature(self, comm_instance, parsed_temperatures, *args, **kwargs):
		current_temp = parsed_temperatures['B'][0]
		if current_temp >= self.maxtemp:
			self._bedpower(0)

		return parsed_temperatures

	@octoprint.plugin.BlueprintPlugin.route("/heatbedsavety", methods=["GET"])
	def myreponse(self):
		data = request.values["data"]
		if data == "boot":
			self._plugin_manager.send_plugin_message(self._identifier, dict(bedpower=self._powerup))
		elif data == "toggle":
			self._bedpower(self._powerup ^ 1)
		return jsonify(success=True)

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
		# for details.
		return dict(
			heatbedsavety=dict(
				displayName="HeatBedSavety Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="linux-paul",
				repo="OctoPrint-Heatbedsavety",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/linux-paul/OctoPrint-Heatbedsavety/archive/{target_version}.zip"
			)
		)


__plugin_name__ = "Heatbedsavety"
__plugin_pythoncompat__ = ">=2.7,<4"


def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = HeatBedSavetyPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.comm.protocol.temperatures.received": __plugin_implementation__.readtemperature,
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}
