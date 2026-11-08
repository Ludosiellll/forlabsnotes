import matplotlib.pyplot as plt
import pathlib

out_dir = pathlib.Path(__file__).parent

languages = ['Python', 'C', 'C++', 'Java', 'C#', 'JavaScript', 'Go', 'SQL', 'Rust', 'PHP']
shares = [15.8, 9.6, 9.2, 8.7, 6.8, 3.4, 2.4, 2.1, 1.8, 1.5]

languages_rev = languages[::-1]
shares_rev = shares[::-1]

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(10, 6), dpi=200)

colors = ['#1f77b4', '#aec7e8', '#ff7f0e', '#2ca02c', '#98df8a', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#17becf'][::-1]
bars = ax.barh(languages_rev, shares_rev, color=colors, edgecolor='#333333', height=0.65)

for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.25, bar.get_y() + bar.get_height()/2, f'{w:.1f}%', ha='left', va='center', fontsize=10, weight='bold', color='#222222')

ax.set_xlim(0, 18.5)
ax.set_xlabel('Индекс популярности (доля запросов и упоминаний, %)', fontsize=11, labelpad=10)
ax.set_title('Рейтинг популярности Топ-10 современных языков программирования (TIOBE Index)', fontsize=12, pad=15, weight='bold')
ax.grid(axis='x', linestyle='--', alpha=0.6)
ax.set_axisbelow(True)

plt.tight_layout()
fig.savefig(out_dir / 'chart_languages_rating.png')
print('Saved chart_languages_rating.png')
