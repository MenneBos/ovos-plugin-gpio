#### Note:
# this script is intented to emit a wakeword message on the internal voice-relay bus (fakebus)
# It uses the hivemind-voice-relay Get_Bus functionality to connect with the fakebus
# 


# buttonpress script requires ovos to be part of groep gpio
echo
source /home/ovos/voice-relay/bin/activate
pip install lgpio, gpiozero

echo "Checking if access is permitted for the gpio groups..."
ls -l /dev/gpiochip*
groups

echo "If ovos is not part of gpio,then add 'ovos' to group 'gpio' to access /dev/gpiochip*..."
sudo usermod -aG gpio ovos
# Save current working directory
CWD=$(pwd)

# Restart the shell
exec bash --login
cd "$CWD"

# # Install the button app?
pip install git+"https://github.com/MenneBos/ovos-plugin-gpio.git"

echo "Running button press test script..."