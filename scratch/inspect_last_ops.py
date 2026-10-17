from ai_edge_litert.interpreter import Interpreter

interp = Interpreter(model_path='/mnt/c/voice_cloning/android/app/src/main/assets/indicf5_dit_int8.tflite')
interp.allocate_tensors()

ops = interp._get_ops_details()
print(f'Total ops: {len(ops)}')
for i, op in enumerate(ops[-15:]):
    idx = len(ops) - 15 + i
    print(f'Op {idx}: {op["op_name"]}, inputs={op["inputs"]}, outputs={op["outputs"]}')
