#!/usr/bin/env python3
"""
GPU Test Script for RTX 5070 TI
Tests PyTorch GPU functionality and compatibility.
"""

import torch
import warnings

def test_gpu_compatibility():
    """Test GPU compatibility and functionality."""
    print("=== PyTorch GPU Compatibility Test ===")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU device count: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            print(f"GPU {i}: {props.name}")
            print(f"  Memory: {props.total_memory / 1024**3:.1f} GB")
            print(f"  Compute capability: {props.major}.{props.minor}")
        
        # Test basic tensor operations
        print("\n=== Testing GPU Operations ===")
        try:
            # Suppress the known compatibility warning for cleaner output
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message=".*CUDA capability.*")
                
                # Simple tensor test
                x = torch.randn(3, 3, device='cuda')
                y = torch.randn(3, 3, device='cuda')
                z = torch.matmul(x, y)
                
                print("✓ Basic tensor operations work")
                print(f"Result shape: {z.shape}")
                print(f"Device: {z.device}")
                
        except RuntimeError as e:
            if "no kernel image is available" in str(e):
                print("✗ GPU operations fail: RTX 5070 TI requires PyTorch with sm_120 support")
                print("  Current PyTorch build doesn't support CUDA capability sm_120")
                print("  This is expected until PyTorch adds RTX 5070 TI support")
            else:
                print(f"✗ GPU operations fail: {e}")
    else:
        print("✗ CUDA not available")

if __name__ == "__main__":
    test_gpu_compatibility()
