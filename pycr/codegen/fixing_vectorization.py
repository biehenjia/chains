import llvmlite.binding as lb


print(lb.get_host_cpu_name())
features = (lb.get_host_cpu_features())
print(features.get('neon',False))
print(features.get('fp-armv8',False))
print(features.get('fullfp16',False))


import subprocess
result = subprocess.run(['sysctl', '-a', 'hw.optional'], capture_output=True, text=True)
print(result.stdout)

