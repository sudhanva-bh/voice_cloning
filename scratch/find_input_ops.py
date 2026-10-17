from ai_edge_litert.interpreter import Interpreter

interp = Interpreter(model_path='/mnt/c/voice_cloning/android/app/src/main/assets/indicf5_dit_int8.tflite')
interp.allocate_tensors()

ops = interp._get_ops_details()
print('Ops using input 0 (x):')
for i, op in enumerate(ops):
    if 0 in op['inputs']:
        print(f"  Op {i}: {op['op_name']}, inputs={op['inputs']}, outputs={op['outputs']}")

print('Ops using input 1 (cond):')
for i, op in enumerate(ops):
    if 1 in op['inputs']:
        print(f"  Op {i}: {op['op_name']}, inputs={op['inputs']}, outputs={op['outputs']}")

print('Ops using input 2 (text):')
for i, op in enumerate(ops):
    if 2 in op['inputs']:
        print(f"  Op {i}: {op['op_name']}, inputs={op['inputs']}, outputs={op['outputs']}")

print('Ops using input 3 (t):')
for i, op in enumerate(ops):
    if 3 in op['inputs']:
        print(f"  Op {i}: {op['op_name']}, inputs={op['inputs']}, outputs={op['outputs']}")
