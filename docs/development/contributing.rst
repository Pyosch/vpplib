Contributing
============

Thank you for considering contributing to vpplib! This document provides guidelines and instructions for contributing to the project.

Setting Up Development Environment
--------------------------------

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/Pyosch/vpplib.git
      cd vpplib

2. Create a virtual environment:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install the package in development mode:

   .. code-block:: bash

      pip install -e .

4. Install development dependencies:

   .. code-block:: bash

      pip install -r requirements-dev.txt

Code Style
---------

We follow the PEP 8 style guide for Python code. Please ensure your code adheres to this style guide.

You can use tools like flake8 and black to check and format your code:

.. code-block:: bash

   flake8 vpplib
   black vpplib

Documentation
------------

We use Sphinx for documentation. Please document your code using docstrings in the NumPy or Google style.

To build the documentation locally:

.. code-block:: bash

   cd docs
   make html

The documentation will be available in the `_build/html` directory.

Testing
------

We use pytest for testing. Please write tests for your code and ensure that all tests pass before submitting a pull request.

To run the tests:

.. code-block:: bash

   pytest

Pull Request Process
------------------

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes
4. Write tests for your changes
5. Update the documentation if necessary
6. Run the tests to ensure they pass
7. Submit a pull request

When submitting a pull request, please provide a clear description of the changes you've made and the problem they solve.

Issue Reporting
-------------

If you find a bug or have a feature request, please create an issue on GitHub. Please include as much information as possible, such as:

* A clear and descriptive title
* A detailed description of the issue or feature request
* Steps to reproduce the issue (if applicable)
* Expected behavior
* Actual behavior
* Screenshots (if applicable)
* Environment information (operating system, Python version, etc.)

Code of Conduct
-------------

Please be respectful and considerate of others when contributing to the project. We strive to create a welcoming and inclusive environment for all contributors.

License
------

By contributing to vpplib, you agree that your contributions will be licensed under the project's license.