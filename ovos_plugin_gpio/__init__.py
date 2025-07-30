from gpiozero import Button
from lgio
from ovos_plugin_manager.phal import PHALPlugin
from ovos_utils.log import LOG
from ovos_bus_client.message import Message

class GPIOInputs(PHALPlugin):
    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="voice_relay-phal-plugin-switches", config=config)
        self.action_btn = Button(27, pull_up=False, bounce_time=0.2)
        self.action_btn.when_pressed = self.on_button_press
        LOG.debug("GPIOZero Action Button initiated on GPIO 27")

    def on_button_press(self):
        self.bus.emit(Message("mycroft.mic.listen"))
        LOG.debug("Mic listening message sent to internal bus")