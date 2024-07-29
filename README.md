# Random Number Generator 2024
This project aims to generate random numbers using various methods to achieve the best possible randomness with existing computer hardware.

## Why True Random Generation is Hard
True random number generation is challenging because computers are deterministic machines, meaning they follow specific instructions to produce predictable results. True randomness, on the other hand, is unpredictable and lacks any discernible pattern. While hardware-based solutions can produce random numbers by leveraging physical processes, achieving true randomness in software alone is difficult.

## Methods of Random Number Generation
This program uses the following methods to generate random numbers:

Entropy Pool Random:

Utilizes the os.urandom function to gather random bytes from the operating system's entropy pool.
Converts these bytes into an integer to produce a random number within a specified range.
Intel Hardware RNG:

Uses Intel's hardware-based random number generator (RDRAND) to produce random numbers.
This method is supported only on Windows systems and requires specific Intel hardware.
OS urandom Hardware Random:

Similar to the Entropy Pool method, this uses os.urandom to generate random bytes.
Converts these bytes into a random number within a given range.
AMD Hardware RNG (placeholder):

Intended to use AMD's hardware-based random number generator.
This method is currently a placeholder and will be implemented in future updates.
Usage
GUI
The program includes a graphical user interface (GUI) for easy interaction.

Code Example
Here is an example of how to use the RandomNumberGenerator class to generate random numbers:

<code>
from random_number_2024 import RandomNumberGenerator

rng = RandomNumberGenerator()

# Generate a random number using the entropy pool method
random_number = rng.generate_entropy_pool_random(1, 100)
print(f"Random number (Entropy Pool): {random_number}")

# Generate a random number using Intel Hardware RNG
try:
    random_number = rng.generate_intel_hardware_random(1, 100)
    print(f"Random number (Intel Hardware RNG): {random_number}")
except OSError as e:
    print(f"Intel Hardware RNG error: {e}")

# Generate a random number using os.urandom
random_number = rng.generate_os_urandom_hardware_random(1, 100)
print(f"Random number (os.urandom): {random_number}")

#Installation
Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/random_number_2024.git
cd random_number_2024
Install the required dependencies:

bash
Copy code
pip install -r requirements.txt
Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

License
This project is licensed under the MIT License. See the LICENSE file for details.
