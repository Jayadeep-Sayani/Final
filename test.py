import numpy as np

def count_strings_in_columns(array):
    # Initialize an empty dictionary to store counts
    string_count = {}
    
    # Get the number of columns
    num_columns = len(array[0])
    
    # Iterate through each column
    for col_idx in range(num_columns):
        # Use a set to store unique strings in the current column
        unique_strings = set(row[col_idx] for row in array)
        
        # Update the dictionary with counts
        for string in unique_strings:
            if string in string_count:
                string_count[string] += 1
            else:
                string_count[string] = 1
    
    return string_count


# Example usage
array = np.array([
    ['banana', 'banana', 'cherry'],
    ['apple', 'apple', 'apple'],
    ['cherry', 'cherry', 'banana']
])

result = count_strings_in_columns(array)
print(result)
