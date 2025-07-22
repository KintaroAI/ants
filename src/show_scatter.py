import matplotlib.pyplot as plt
import numpy as np

# Prepare buckets for survived colonies
bucket_count = 10
bucket_size = 10
bucket_x = [[] for _ in range(bucket_count)]
bucket_y = [[] for _ in range(bucket_count)]

# For dead colonies and max step
x_dead = []
y_dead = []
x_max = []
y_max = []

FILE_NAME = './results.txt'

with open(FILE_NAME, 'r') as input:
    for line in input:
        ants, food, step, colony_a_is_alive, colony_b_is_alive = [
            int(i) for i in line.strip().split(',')]
        if step == 500000:
            x_max.append(food)
            y_max.append(step)
            continue
        if colony_a_is_alive and colony_b_is_alive:
            # Bucket by number of ants (1-10, 11-20, ..., 91-100)
            bucket_idx = min((ants - 1) // bucket_size, bucket_count - 1)
            bucket_x[bucket_idx].append(food)
            bucket_y[bucket_idx].append(step)
        else:
            x_dead.append(food)
            y_dead.append(step)

# Vibrant colors for buckets
cmap = plt.get_cmap('tab10')
bucket_colors = [cmap(i) for i in range(bucket_count)]

# Plot survived buckets
for i in range(bucket_count):
    plt.scatter(bucket_x[i], bucket_y[i], color=bucket_colors[i], label=f'Ants {i*bucket_size+1}-{(i+1)*bucket_size}')

# Plot dead colonies and max step
plt.scatter(x_dead, y_dead, color='red', label='Colony died')
plt.scatter(x_max, y_max, color='gray', label='Max steps')

plt.title('Ant clustering by ant count buckets')
plt.xlabel('Amount of food')
plt.ylabel('Time')
plt.legend()
plt.show()