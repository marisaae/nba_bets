import plotly.graph_objects as go
import pandas as pd

def render_prop_chart(last_5_stats, prop_line, market, prediction):
    max_range = last_5_stats[market].max()

    diff = abs(prediction - prop_line)
    offset = 6 if diff < .5 else 0

    stats = last_5_stats[market]
    avg_stat = stats.mean().round(1)
    opp = last_5_stats["matchup"].str.split().str[-1]
    dates = pd.to_datetime(last_5_stats["game_date"]).dt.strftime("%m/%d")

    x_labels = [f"<b>{o}</b><br>{d}" for o, d in zip(opp, dates)]

    colors = ['red' if val < prop_line
              else 'gray' if val == prop_line 
              else 'green' 
              for val in stats]
    
    fig = go.Figure(
            [go.Bar(
                x=x_labels, 
                y=stats,
                marker_color=colors,
                meta=market,
                hovertemplate=("%{meta}: %{y}<extra></extra>"),
                texttemplate="%{y}",
                textposition="inside",
                textfont=dict(size=18)
                )
            ])
    
    fig.update_xaxes(title_text=f"<b>{avg_stat}</b> avg last 5",title_font_color="black", title_font_size=18,autorange="reversed", linecolor='black', linewidth=1, tickfont=dict(size=14))
    fig.update_yaxes(title_text=f"{market}", title_font_color="black", linecolor='black', linewidth=1, range=[0, max_range + 5])

    fig.add_hline(
        y=prop_line,
        line_dash="dot",
        line_color="black"
    )

    last_x = x_labels[0]
    fig.add_annotation(
        x=last_x,
        y=prop_line,
        xref="x",
        yref="y",
        text=f"Prop Line: <b>{prop_line}</b>",
        showarrow=False,
        xanchor="left",
        yanchor="middle",
        xshift=50,
        yshift=offset,
        font=dict(size=14, color="black"),
        bgcolor="white"
    )

    fig.add_hline(
        y=prediction,
        line_dash="longdash",
        line_color="black"
    )
    fig.add_annotation(
        x=last_x,
        y=prediction,
        xref="x",
        yref="y",
        text=f"Prediction: <b>{prediction}</b>",
        showarrow=False,
        xanchor="left",
        yanchor="middle",
        xshift=50,
        yshift=-(offset),
        font=dict(size=14, color="black"),
        bgcolor="white"
    )

    fig.update_layout(
        title={
        'text': f"{market} Last 5 Games",
        'y': 0.9,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 20, 'color': 'black'}
        },
        barcornerradius=15,
        height=600,
        width=600, 
        showlegend=False
        )
    return fig