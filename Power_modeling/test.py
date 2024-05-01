import numpy as np

all_indices = np.arange(21)
print(all_indices)

print(all_indices[np.logical_or((all_indices % 7 == 6),(all_indices % 7 == 5))])
