import subprocess

# command to set pin 7 to pwm
set_pwm_pin = ["gpio","mode","23","pwm"]

# command to set the duty cycle
set_pwm_dc = ["gpio","pwm","23","50"]

# command to change to ms mode
set_pwm_ms = ["gpio","pwm-ms"]

# command to set mr
set_pwm_mr = ["gpio","pwmr", "4000"]

# command to set mc
set_pwm_mr = ["gpio","pwmc", "4000"]

# command to show pin status
pin_read = ["gpio","readall"]

# run all commands
subprocess.run(set_pwm_pin, shell=True)
subprocess.run(set_pwm_dc, shell=True)
subprocess.run(set_pwm_ms, shell=True)
subprocess.run(set_pwm_mc, shell=True)
subprocess.run(set_pwm_mr, shell=True)
subprocess.run(pin_read, shell=True)

