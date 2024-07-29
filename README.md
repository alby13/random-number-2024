# Random Number Generator 2024
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

This project aims to generate random numbers using various methods to achieve the best possible randomness with existing computer hardware.

## Why True Random Generation is Hard
True random number generation is challenging because computers are deterministic machines, meaning they follow specific instructions to produce predictable results. True randomness, on the other hand, is unpredictable and lacks any discernible pattern. While hardware-based solutions can produce random numbers by leveraging physical processes, achieving true randomness in software alone is difficult.

## Methods of Random Number Generation
This program uses the following methods to generate random numbers:

**Entropy Pool Random:**

Utilizes the os.urandom function to gather random bytes from the operating system's entropy pool.
Converts these bytes into an integer to produce a random number within a specified range.

**Intel Processor Method:**

Uses Intel's hardware-based random number generator (RDRAND) to produce random numbers.
This method is supported only on Windows systems and requires specific Intel hardware.

**OS urandom Hardware Method:**

This method uses the operating system's urandom function to generate a random number. The urandom function uses a combination of hardware and software-based random number generators to generate random numbers. os.urandom generates random bytes and converts these bytes into a random number.

**AMD Processor Method:**

This method uses AMD's Hardware Random Number Generator (HRNG) to generate a random number. The HRNG is a hardware-based random number generator that uses thermal noise to generate random numbers. This method is considered to be highly random and secure, but it is only available on AMD processors.

# Download the program

### Clone the repository:

<code>bash
Copy code
git clone https://github.com/alby13/random_number_2024.git
cd random_number_2024</code>

### Install the required dependencies:

<code>bash
Copy code
pip install -r requirements.txt</code>

### It's easy to use because a graphical menu is provided.

### Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

# License
This project is licensed under the MIT License.
