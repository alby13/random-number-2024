import tkinter as tk
from tkinter import ttk, messagebox
import os
import struct
import ctypes
from ctypes import c_uint64, CFUNCTYPE, POINTER, wintypes
import threading
import platform
import logging

# Constants from AMD's code
SECRNG_SUPPORTED = 1
SECRNG_SUCCESS = 0
RDRAND_RETRY_COUNT = 10

# Logger
logging.basicConfig(level=logging.INFO)

class RandomNumberGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate_entropy_pool_random(self, min_value: int, max_value: int) -> int:
        """Generate a random number using the entropy pool"""
        random_bytes = os.urandom(8)
        random_long = struct.unpack('Q', random_bytes)[0]
        return min_value + (random_long % (max_value - min_value + 1))

    def generate_intel_hardware_random(self, min_value: int, max_value: int) -> int:
        if platform.system() != 'Windows':
            raise OSError("Intel Hardware RNG is only supported on Windows")

        def setup_rdrand():
            RDRAND_FUNC = CFUNCTYPE(ctypes.c_bool, ctypes.POINTER(c_uint64))
            asm_code = b"\x48\x31\xC0\x0F\xC7\xF0\x48\x89\x07\x0F\x92\xC0\xC3"
            return self.setup_asm_function(asm_code, RDRAND_FUNC)

        try:
            rdrand_func = setup_rdrand()
        except Exception as e:
            raise RuntimeError(f"Failed to set up Intel RDRAND: {e}")

        result = c_uint64()
        if not rdrand_func(ctypes.byref(result)):
            raise RuntimeError("Intel RDRAND instruction failed")

        return min_value + (result.value % (max_value - min_value + 1))

    def generate_crypto_hardware_random(self, min_value: int, max_value: int) -> int:
        """Generate a random number using os.urandom"""
        try:
            random_bytes = os.urandom(8)
            random_long = struct.unpack('Q', random_bytes)[0]
            return min_value + (random_long % (max_value - min_value + 1))
        except Exception as e:
            print(f"Error: {e}")
            return None

    def generate_amd_hardware_random(self, min_value: int, max_value: int) -> int:
        """Generate a random number using AMD Hardware RNG"""

class RandomNumberGeneratorGUI:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("Random Number Generator")
        self.master.geometry("1500x400")

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.logger = logging.getLogger(__name__)  # Create a logger attribute

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

        self.entropy_frame = self.create_generator_frame(main_frame, "Entropy Pool Generator", 0)
        self.intel_frame = self.create_generator_frame(main_frame, "Intel Hardware Generator", 1)
        self.on_random_frame = self.create_generator_frame(main_frame, "CryptGenRandom win32crypt Generator", 2)
        self.amd_frame = self.create_generator_frame(main_frame, "AMD Hardware Generator", 3)

        for i in range(4):
            main_frame.grid_columnconfigure(i, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

    def create_generator_frame(self, parent, title, column):
        frame = ttk.LabelFrame(parent, text=title, padding="10")
        frame.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")

        description = ""
        if "Entropy" in title:
            description = "Using the operating system's entropy pool. The entropy pool is a collection of random data gathered from various sources, such as keyboard and mouse input, network packets, and disk I/O. This method is considered to be highly random and secure."
        elif "Intel" in title:
            description = "Using Intel's Hardware Random Number Generator (HRNG). The HRNG is a hardware-based random number generator that uses thermal noise to generate random numbers. This method is considered to be highly random and secure, but it is only for Intel processors."
        elif "Crypt" in title:
            description = "Uses Windows's CryptGenRandom from win32crypt to generate a random number. It fills a buffer with cryptographically random bytes. An integer (number) is generated from the bytes."
        elif "AMD" in title:
            description = "Uses AMD's Hardware Random Number Generator (HRNG) to generate a random number. The HRNG is a hardware-based random number generator that uses thermal noise to generate random numbers. Highly random and secure, but it is only for AMD processors."

        ttk.Label(frame, text=description, wraplength=200).grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        ttk.Label(frame, text="Min:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        min_var = tk.IntVar(value=1)
        min_entry = ttk.Entry(frame, textvariable=min_var, width=10)
        min_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(frame, text="Max:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        max_var = tk.IntVar(value=100)
        max_entry = ttk.Entry(frame, textvariable=max_var, width=10)
        max_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        result_var = tk.StringVar(value="Result: ")
        result_label = ttk.Label(frame, textvariable=result_var, wraplength=200)
        result_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        if "Intel" in title:
            generate_func = self.generate_intel_hardware_random
        elif "Operating" in title:
            generate_func = self.generate_crypto_hardware_random
        elif "AMD" in title:
            generate_func = self.generate_amd_hardware_random
        else:
            generate_func = self.generate_entropy_pool_random

        generate_button = ttk.Button(frame, text="Generate", 
                                     command=lambda: self.generate_wrapper(generate_func, min_var, max_var, result_var, generate_button))
        generate_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        for child in frame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

        return frame

    def generate_wrapper(self, generate_func, min_var, max_var, result_var, button):
        def task():
            button.config(state="disabled")
            result_var.set("Generating...")
            self.master.update_idletasks()
            try:
                min_val, max_val = min_var.get(), max_var.get()
                if min_val >= max_val:
                    raise ValueError("Min value must be less than Max value")
                result = generate_func(min_val, max_val)
                result_var.set(f"Result: {result}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                result_var.set("Error occurred")
            finally:
                button.config(state="normal")

        threading.Thread(target=task, daemon=True).start()

    def generate_entropy_pool_random(self, min_value, max_value):
        random_bytes = os.urandom(8)
        random_long = struct.unpack('Q', random_bytes)[0]
        return min_value + (random_long % (max_value - min_value + 1))

    def generate_intel_hardware_random(self, min_value, max_value):
        if platform.system() != 'Windows':
            raise OSError("Intel Hardware RNG is only supported on Windows")

        def setup_rdrand():
            RDRAND_FUNC = CFUNCTYPE(ctypes.c_bool, ctypes.POINTER(c_uint64))
            asm_code = b"\x48\x31\xC0\x0F\xC7\xF0\x48\x89\x07\x0F\x92\xC0\xC3"
            return self.setup_asm_function(asm_code, RDRAND_FUNC)

        try:
            rdrand_func = setup_rdrand()
        except Exception as e:
            raise RuntimeError(f"Failed to set up Intel RDRAND: {e}")

        result = c_uint64()
        if not rdrand_func(ctypes.byref(result)):
            raise RuntimeError("Intel RDRAND instruction failed")

        return min_value + (result.value % (max_value - min_value + 1))

    def generate_crypto_hardware_random(self, min_value, max_value):
        hCryptProv = ctypes.wintypes.HANDLE()
        crypt_acquire_context = ctypes.windll.advapi32.CryptAcquireContextW
        crypt_gen_random = ctypes.windll.advapi32.CryptGenRandom
        crypt_release_context = ctypes.windll.advapi32.CryptReleaseContext

        if crypt_acquire_context(ctypes.byref(hCryptProv), None, None, 1, 0xF0000000):
            buf = ctypes.create_string_buffer(8)
            if crypt_gen_random(hCryptProv, len(buf), buf):
                random_number = int.from_bytes(buf.raw, 'big')
            else:
                error_code = ctypes.windll.kernel32.GetLastError()
                crypt_release_context(hCryptProv, 0)
                raise OSError(f"Failed to generate random number on Windows, error code: {error_code}")
            crypt_release_context(hCryptProv, 0)
        else:
            error_code = ctypes.windll.kernel32.GetLastError()
            raise OSError(f"Failed to acquire cryptographic context on Windows, error code: {error_code}")

    def generate_amd_hardware_random(self, min_value, max_value):
        def get_rdrand64u(rng64, retry_count):
            RDRAND_FUNC = CFUNCTYPE(ctypes.c_int, POINTER(c_uint64), ctypes.c_int)
            asm_code = b"\x48\x31\xC0\x0F\xC7\xF0\x74\x03\xB0\x01\xC3\x31\xC0\xC3"
            rdrand_func = self.setup_asm_function(asm_code, RDRAND_FUNC)
            return rdrand_func(rng64, retry_count)

        try:
            rng64 = c_uint64()
            ret = get_rdrand64u(ctypes.byref(rng64), 10)  # 10 retries

            if ret != SECRNG_SUCCESS:
                raise RuntimeError("AMD RDRAND instruction failed")

            return min_value + (rng64.value % (max_value - min_value + 1))

        except Exception as e:
            self.logger.error(f"Failed to generate random number using AMD RDRAND: {e}")

        try:
            # Load the advapi32 library
            advapi32 = ctypes.windll.advapi32

            # Define the CryptGenRandom function prototype
            CryptGenRandom = advapi32.CryptGenRandom
            CryptGenRandom.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(ctypes.c_char)]
            CryptGenRandom.restype = wintypes.BOOL

            # Create a handle to the CryptGenRandom API
            hCryptProv = ctypes.c_void_p()

            # Generate random numbers using the CryptGenRandom API
            random_bytes = ctypes.create_string_buffer(8)
            CryptGenRandom(hCryptProv, 8, random_bytes)

            # Convert the random bytes to a long integer
            random_long = struct.unpack('Q', random_bytes.raw)[0]

            # Return the random number
            return min_value + (random_long % (max_value - min_value + 1))

        except Exception as e:
            self.logger.error(f"Failed to generate random number using AMD CryptGenRandom: {e}")

        def get_rdrand64u(rng64, retry_count):
            RDRAND_FUNC = CFUNCTYPE(ctypes.c_int, POINTER(c_uint64), ctypes.c_int)
            asm_code = b"\x48\x31\xC0\x0F\xC7\xF0\x74\x03\xB0\x01\xC3\x31\xC0\xC3"
            rdrand_func = self.setup_asm_function(asm_code, RDRAND_FUNC)
            return rdrand_func(rng64, retry_count)

        #if not is_RDRAND_supported():
        #    raise RuntimeError("RDRAND is not supported on this AMD processor")

        rng64 = c_uint64()
        ret = get_rdrand64u(ctypes.byref(rng64), 10)  # 10 retries

        if ret != SECRNG_SUCCESS:
            raise RuntimeError("AMD RDRAND instruction failed")

        return min_value + (rng64.value % (max_value - min_value + 1))

    def setup_asm_function(self, asm_code, func_type):
        code_buffer = ctypes.create_string_buffer(asm_code)
        
        kernel32 = ctypes.windll.kernel32
        size = len(asm_code)
        kernel32.VirtualAlloc.restype = ctypes.c_void_p
        kernel32.VirtualAlloc.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_ulong, ctypes.c_ulong]
        addr = kernel32.VirtualAlloc(None, size, 0x1000, 0x40)
        if not addr:
            raise OSError("Failed to allocate memory")
        
        ctypes.memmove(addr, code_buffer, size)
        return func_type(addr)

if __name__ == "__main__":
    root = tk.Tk()
    app = RandomNumberGeneratorGUI(root)
    root.mainloop()
