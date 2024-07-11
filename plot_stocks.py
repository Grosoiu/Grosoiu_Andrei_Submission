import os
import scipy.io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Define paths for the I/O directories and for the folder where the coefficients are stored
inputs_dir = os.path.join(os.getcwd(), 'inputs')
poly_coef_dir = os.path.join(os.getcwd(), 'polynomialCoef')
output_dir = os.path.join(os.getcwd(), 'output')

os.makedirs(output_dir, exist_ok=True)

# Extract the third column from the csv files
def load_stock_values(file_path):
    df = pd.read_csv(file_path, header=None)
    stock_values = df.iloc[:, 2].values
    return stock_values

# Load the coefficients generated in Matlab into memory
def load_polynomial_coefficients(stock_name):
    file_path = os.path.join(poly_coef_dir, f"{stock_name}_poly_coeffs.mat")
    mat = scipy.io.loadmat(file_path)
    coefficients = mat['p'][0]
    return coefficients

# Plot the values of the stock and the quartic function that approximates the stock value
def plot_stock_and_polynomial(stock_name, stock_values, coefficients):
    x = np.arange(1, len(stock_values) + 1)
    x_fit = np.linspace(min(x), max(x), 100)
    fitted_values = np.polyval(coefficients, x_fit)
    
    plt.figure()
    plt.plot(x, stock_values, 'o', label='Original Data') # the stock values
    plt.plot(x_fit, fitted_values, '-', label='Polynomial Fit')  # Polynomial Function
    plt.xlabel('Index')
    plt.ylabel('Stock Value')
    plt.title(f'{stock_name} Stock Values and Polynomial Fit')
    plt.legend()
    
    # Save the plot as a png file to the output directory
    output_file = os.path.join(output_dir, f'{stock_name}_fitting.png')
    plt.savefig(output_file)
    plt.close()

# Get the data from each csv file in the input directory
# os.walk returns 3 values dirpath, dirnames and filenames
for root, _, files in os.walk(inputs_dir):
    for file in files:
        if file.endswith(".csv"):
            stock_name = os.path.splitext(file)[0] # get the name of the stock
            file_path = os.path.join(root, file)
            
            # Load stock values and polynomial coefficients
            stock_values = load_stock_values(file_path)
            coefficients = load_polynomial_coefficients(stock_name)
            
            # Plot stock values and polynomial
            plot_stock_and_polynomial(stock_name, stock_values, coefficients)
