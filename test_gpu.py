# test_gpu_compute.py
import torch
import time

print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    # Force GPU usage despite warning
    device = torch.device("cuda:0")
    
    # Simple computation test
    x = torch.randn(1000, 1000).to(device)
    y = torch.randn(1000, 1000).to(device)
    
    # Warmup
    z = torch.matmul(x, y)
    torch.cuda.synchronize()
    
    # Timed test
    start = time.time()
    for _ in range(100):
        z = torch.matmul(x, y)
    torch.cuda.synchronize()
    end = time.time()
    
    print(f"\nGPU computation successful!")
    print(f"100 matrix multiplications: {end-start:.3f} seconds")
    print(f"GPU memory used: {torch.cuda.memory_allocated()/1024**2:.1f} MB")
    
    # Test training operations
    model = torch.nn.Linear(100, 100).to(device)
    data = torch.randn(32, 100).to(device)
    output = model(data)
    loss = output.sum()
    loss.backward()
    
    print("Backpropagation successful!")
