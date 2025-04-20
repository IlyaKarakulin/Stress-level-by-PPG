import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('/home/artem/Documents/2_course/Project_ML/stress-level-by-PPG/discovery/testing.csv')  

plt.style.use('ggplot')

fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.bar(
    data['state'], 
    data['stress_index_0-5'],
    color=['#25DE43', '#C93D6C', '#25DE43', '#C93D6C', '#C93D6C'],  #
    width=0.6
)

ax.set_ylim(0, 5)
ax.set_title('Stress Index by State', pad=20, fontsize=14)
ax.set_xlabel('State', labelpad=10)
ax.set_ylabel('Stress Index (0-5)', labelpad=10)

for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  
                textcoords="offset points",
                ha='center', va='bottom')


ax.yaxis.grid(True, linestyle='--', alpha=0.7)

plt.tight_layout()

plt.savefig("data2.png")
plt.show()