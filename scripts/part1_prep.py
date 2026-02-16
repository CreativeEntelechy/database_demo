import os
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


DATA_PATH = Path("data/Part1/Fall to Spring Loss FICTIONAL.csv")
OUTPUT_DIR = Path("outputs")


def categorize_major(title):
    """Categorize program title into academic discipline."""
    title = str(title).lower()
    if 'nursing' in title or 'health' in title or 'bio' in title or 'chem' in title:
        return 'STEM & Health Professions'
    elif 'business' in title or 'accounting' in title or 'marketing' in title or 'finance' in title:
        return 'Business & Finance'
    elif 'social work' in title or 'psych' in title or 'sociology' in title:
        return 'Social Sciences'
    elif 'non-degree' in title:
        return 'Non-Degree'
    else:
        return 'Arts, Humanities & Other'


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load and Clean Data
    df = pd.read_csv(DATA_PATH)
    df.fillna('NA', inplace=True)

    # 2. Feature Engineering: Group programs into Academic Disciplines
    df['Academic_Discipline'] = df['STP_PROGRAM_TITLE'].apply(categorize_major)

    # 3. Feature Engineering: Flag Extracurricular/Athletic Time Demands
    df['Is_Special_Cohort'] = df['ATHLETIC_STATUS'].apply(
        lambda x: 'Special/Athletic Cohort' if x != 'NA' else 'No Affiliation'
    )

    # 4. Aggregate Data for the Visual
    plot_df = df.groupby(['Academic_Discipline', 'Is_Special_Cohort']).size().unstack(fill_value=0)
    plot_df['Total'] = plot_df.sum(axis=1)
    plot_df = plot_df.sort_values('Total', ascending=True).drop(columns='Total')

    # 5. Create the Visualization
    sns.set_theme(style="whitegrid", context="talk")
    fig, ax = plt.subplots(figsize=(12, 7))

    plot_df.plot(kind='barh', stacked=True, ax=ax, color=['#d3d3d3', '#1f77b4'])

    ax.set_title('Fall to Spring Attrition:\nConcentration in STEM/Health and Special Cohorts', 
                 fontsize=16, pad=20, weight='bold')
    ax.set_xlabel('Number of Students Lost', fontsize=12, weight='bold')
    ax.set_ylabel('Academic Discipline', fontsize=12, weight='bold')

    # Add Annotations
    for p in ax.patches:
        width, height = p.get_width(), p.get_height()
        x, y = p.get_xy() 
        if width > 0:
            ax.text(x + width/2, 
                    y + height/2, 
                    '{:.0f}'.format(width), 
                    horizontalalignment='center', 
                    verticalalignment='center',
                    color='white' if p.get_facecolor()[0] < 0.5 else 'black',
                    fontsize=11)

    plt.legend(title='Student Affiliation', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'part1_retention_insight.png', dpi=300)
    plt.close()

    # Export Summary Table for Power BI Use
    df.to_csv(OUTPUT_DIR / 'summary_table.csv', index=False)


if __name__ == "__main__":
    main()
