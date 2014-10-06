from reaver_toolkit import AiroDump

a = AiroDump()

print a.networks
a.refresh_networks()
print a.networks