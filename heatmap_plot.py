import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from mplsoccer import Pitch

def generate_heatmap(team='both'):
    data = pd.read_csv("tracking_positions.csv")
    data['team'] = data['team'].str.strip().str.lower()

    pitch_length = 105
    pitch_width = 68

    team1_data = data[data['team'] == 'team1']
    team2_data = data[data['team'] == 'team2']

    pitch = Pitch(pitch_type='custom', pitch_length=pitch_length, pitch_width=pitch_width,
                  line_color='white', pitch_color='green')
    fig, ax = pitch.draw(figsize=(10, 6))

    clip_bounds = ((0, pitch_length), (0, pitch_width))

    if team in ['team1', 'both'] and not team1_data.empty:
        sns.kdeplot(
            x=team1_data['x'], y=team1_data['y'],
            fill=True, cmap='Blues', alpha=0.5,
            ax=ax, bw_adjust=0.4, clip=clip_bounds
        )

    if team in ['team2', 'both'] and not team2_data.empty:
        sns.kdeplot(
            x=team2_data['x'], y=team2_data['y'],
            fill=True, cmap='Reds', alpha=0.5,
            ax=ax, bw_adjust=0.4, clip=clip_bounds
        )

    ax.set_xlim(0, pitch_length)
    ax.set_ylim(pitch_width, 0)

    filename = f"heatmap_{team}_teams.png"
    plt.title(f"Player Position Heatmap - {team.capitalize()}", fontsize=14)
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return filename