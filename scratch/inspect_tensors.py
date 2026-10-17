from ai_edge_litert.interpreter import Interpreter

interp = Interpreter(model_path='/mnt/c/voice_cloning/android/app/src/main/assets/indicf5_dit_int8.tflite')
interp.allocate_tensors()
tensors = {t['index']: t for t in interp.get_tensor_details()}
for idx in [362, 385, 402]:
    t = tensors[idx]
    val = interp.get_tensor(idx)
    print(f"Tensor {idx}: {t['name']}, shape={val.shape}, dtype={val.dtype}, min={val.min()}, max={val.max()}")
    if val.size < 20:
        print(f"  val={val}")
