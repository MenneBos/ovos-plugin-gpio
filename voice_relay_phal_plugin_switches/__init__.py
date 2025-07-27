from gpiozero import Button
from time import sleep
from ovos_plugin_manager.phal import PHALPlugin
from ovos_plugin_manager.hardware.switches import AbstractSwitches
from ovos_utils.log import LOG
from hivemind_bus_client.message import Message

class SwitchInputs(PHALPlugin):
    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="voice_relay-phal-plugin-switches", config=config)
        # TODO: Read pins from configuration if needed
        self.switches = GPIOSwitches(
            action_callback=self.on_button_press,
            volup_callback=self.on_button_volup_press,
            voldown_callback=self.on_button_voldown_press,
            mute_callback=self.on_hardware_mute,
            unmute_callback=self.on_hardware_unmute
        )

        # Initial mute state check
        if self.switches.is_muted():
            self.bus.emit(Message('mycroft.mic.mute'))
            LOG.debug("Send message to mute the mic")

        self.bus.on('mycroft.mic.status', self.on_mic_status)
        LOG.debug("ask mic status on internal fakebus")

    def on_mic_status(self, message):
        if self.switches.is_muted():
            msg_type = 'mycroft.mic.mute'
        else:
            msg_type = 'mycroft.mic.unmute'
        self.bus.emit(message.reply(msg_type))
        LOG.debug("Mute/unmute message on internal fakebus")

    def on_button_press(self):
        if not self.switches.is_muted():
            self.bus.emit(Message("mycroft.mic.listen"))
        else:
            self.bus.emit(Message("mycroft.mic.error", {"error": "mic_sw_muted"}))
        LOG.debug("Mic listening message sent to internal bus")

    def on_button_volup_press(self):
        LOG.debug("VolumeUp button pressed")
        self.bus.emit(Message("mycroft.volume.increase"))

    def on_button_voldown_press(self):
        LOG.debug("VolumeDown button pressed")
        self.bus.emit(Message("mycroft.volume.decrease"))

    def on_hardware_mute(self):
        LOG.debug("mic HW muted")
        self.bus.emit(Message("mycroft.mic.mute"))

    def on_hardware_unmute(self):
        LOG.debug("mic HW unmuted")
        self.bus.emit(Message("mycroft.mic.unmute"))


class GPIOSwitches(AbstractSwitches):
    def __init__(self, action_callback, volup_callback, voldown_callback,
                 mute_callback, unmute_callback,
                 volup_pin=22, voldown_pin=23, action_pin=24, mute_pin=25,
                 sw_active_state=False, sw_muted_state=True, bounce_time=0.1):
        # sw_active_state: False for pull-up (active low), True for pull-down (active high)
        self.action_btn = Button(action_pin, pull_up=not sw_active_state, bounce_time=bounce_time)
        self.volup_btn = Button(volup_pin, pull_up=not sw_active_state, bounce_time=bounce_time)
        self.voldown_btn = Button(voldown_pin, pull_up=not sw_active_state, bounce_time=bounce_time)
        self.mute_btn = Button(mute_pin, pull_up=not sw_active_state, bounce_time=bounce_time)

        self._muted_state = sw_muted_state
        self._is_muted = False

        self._mute_callback = mute_callback
        self._unmute_callback = unmute_callback

        self.action_btn.when_pressed = action_callback
        self.volup_btn.when_pressed = volup_callback
        self.voldown_btn.when_pressed = voldown_callback

        # Mute/unmute logic: call mute_callback when pressed, unmute_callback when released
        self.mute_btn.when_pressed = self.on_mute_toggle

        LOG.debug("GPIOZero Buttons initiated")

    def is_muted(self):
        # Returns True if mute button is in the muted state
        return self.mute_btn.is_pressed == self._muted_state

    @property
    def capabilities(self) -> dict:
        return {}

    def shutdown(self):
        # gpiozero cleans up automatically, but you can add extra cleanup here if needed
        pass

    def on_mute_toggle(self):
        if self._is_muted:
            self._unmute_callback()
            self._is_muted = False
        else:
            self._mute_callback()
            self._is_muted = True