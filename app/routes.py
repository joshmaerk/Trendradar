from flask import Blueprint, render_template, request, redirect, url_for
from .extensions import db
from .models import (Category, Trend, get_category_angles, time_horizons, phases,
                     time_horizon_radii)

import plotly.graph_objs as go
import plotly.offline as pyo
import numpy as np

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    categories = Category.query.order_by(Category.name).all()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        phase = request.form['phase']
        time_horizon = request.form['time_horizon']
        selected_categories = request.form.getlist('categories')
        
        # Beispiel in der index-Funktion
        relevance = int(request.form['relevance'])
        market_potential = int(request.form['market_potential'])
        likelihood = int(request.form['likelihood'])
        sustainability = int(request.form['sustainability'])
        maturity_level = int(request.form['maturity_level'])

        new_trend = Trend(
            title=title,
            description=description,
            phase=phase,
            time_horizon=time_horizon,
            relevance=relevance,
            market_potential=market_potential,
            likelihood=likelihood,
            sustainability=sustainability,
            maturity_level=maturity_level
        )
        for category_id in selected_categories:
            category = Category.query.get(category_id)
            if category:
                new_trend.categories.append(category)

        db.session.add(new_trend)
        db.session.commit()
        return redirect(url_for('main.index'))

    trends = Trend.query.all()
    fig = create_trend_radar(trends)
    graph_div = pyo.plot(fig, output_type='div', include_plotlyjs=False)
    return render_template(
        'index.html',
        categories=categories,
        time_horizons=time_horizons,
        phases=phases,
        graph_div=graph_div,
        trends=trends
    )

@main_bp.route('/edit/<int:trend_id>', methods=['GET', 'POST'])
def edit_trend(trend_id):
    trend = Trend.query.get_or_404(trend_id)
    categories = Category.query.order_by(Category.name).all()
    if request.method == 'POST':
        trend.title = request.form['title']
        trend.description = request.form['description']
        trend.phase = request.form['phase']
        trend.time_horizon = request.form['time_horizon']
        
        trend.relevance = int(request.form['relevance'])
        trend.market_potential = int(request.form['market_potential'])
        trend.likelihood = int(request.form['likelihood'])
        trend.sustainability = int(request.form['sustainability'])
        trend.maturity_level = int(request.form['maturity_level'])

        selected_categories = request.form.getlist('categories')
        trend.categories = []
        for category_id in selected_categories:
            category = Category.query.get(category_id)
            if category:
                trend.categories.append(category)
        db.session.commit()
        return redirect(url_for('main.trend_detail', trend_id=trend.id))
    all_trends = Trend.query.order_by(Trend.title).all()
    return render_template(
        'edit_trend.html',
        trend=trend,
        categories=categories,
        time_horizons=time_horizons,
        phases=phases,
        all_trends=all_trends
    )

@main_bp.route('/delete/<int:trend_id>', methods=['POST'])
def delete_trend(trend_id):
    trend = Trend.query.get_or_404(trend_id)
    db.session.delete(trend)
    db.session.commit()
    return redirect(url_for('main.index'))

def create_trend_radar(trends):
    data = []
    annotations = []
    category_angles = get_category_angles()

    for trend in trends:
        for category in trend.categories:
            angle = category_angles[category.name]
            radius = time_horizon_radii[trend.time_horizon]

            # Konvertieren des Winkels in Radianten
            angle_rad = np.deg2rad(angle)

            x = radius * np.cos(angle_rad)
            y = radius * np.sin(angle_rad)

            # Größe des Punkts basierend auf der Relevanz
            marker_size = trend.relevance * 2  # Multiplizieren für bessere Sichtbarkeit

            data.append(go.Scatter(
                x=[x], y=[y],
                mode='markers',
                marker=dict(size=marker_size),
                name=trend.title
            ))

            annotations.append(dict(
                x=x, y=y,
                xanchor='left', yanchor='bottom',
                text=trend.title,
                showarrow=False
            ))

    # Erstellen der Formen für das Radar
    shapes = [
        # Kreise für Zeithorizonte
        dict(type='circle', x0=-1, y0=-1, x1=1, y1=1, line=dict(color='black', dash='dot')),
        dict(type='circle', x0=-2, y0=-2, x1=2, y1=2, line=dict(color='black', dash='dot')),
        dict(type='circle', x0=-3, y0=-3, x1=3, y1=3, line=dict(color='black', dash='dot')),
    ]

    # Linien für Kategorietrennungen
    for angle in category_angles.values():
        angle_rad = np.deg2rad(angle)
        x1 = 3 * np.cos(angle_rad)
        y1 = 3 * np.sin(angle_rad)
        shapes.append(dict(
            type='line', x0=0, y0=0, x1=x1, y1=y1, line=dict(color='black', dash='dot')
        ))

    layout = go.Layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
        annotations=annotations,
        shapes=shapes,
        width=600,
        height=600
    )

    fig = go.Figure(data=data, layout=layout)
    return fig

@main_bp.route('/trend/<int:trend_id>', methods=['GET'])
def trend_detail(trend_id):
    trend = Trend.query.get_or_404(trend_id)
    return render_template(
        'trend_detail.html',
        trend=trend,
        all_trends=Trend.query.order_by(Trend.title).all()
    )

from .models import Category, Trend  # Importieren Sie die Modelle
import plotly.graph_objs as go
import numpy as np

def create_trend_radar(trends):
    # Definieren der Kategorienamen
    categories = ['Kategorie A', 'Kategorie B', 'Kategorie C', 'Kategorie D']
    
    # Map Kategorien zu Farben
    category_colors = {
        'Kategorie A': 'rgba(0, 0, 255, 0.1)',      # Blautöne
        'Kategorie B': 'rgba(255, 165, 0, 0.1)',    # Orangetöne
        'Kategorie C': 'rgba(0, 128, 0, 0.1)',      # Grüntöne
        'Kategorie D': 'rgba(128, 128, 128, 0.1)'   # Grautöne
    }
    
    # Winkelbereiche für die Kategorien (jeweils 45 Grad in einem Halbkreis von 180 Grad)
    category_angles = {
        'Kategorie A': (0, 45),
        'Kategorie B': (45, 90),
        'Kategorie C': (90, 135),
        'Kategorie D': (135, 180)
    }
    
    # Hilfsfunktion zur Umrechnung von Grad in Radianten
    def deg_to_rad(deg):
        return deg * (np.pi / 180)
    
    data = []
    shapes = []
    
    # Erstellen der Segmente für die Kategorien
    for category, (start_angle, end_angle) in category_angles.items():
        theta = np.linspace(deg_to_rad(start_angle), deg_to_rad(end_angle), 100)
        x = np.concatenate(([0], np.cos(theta) * 10, [0]))
        y = np.concatenate(([0], np.sin(theta) * 10, [0]))
        
        path = 'M ' + ' L '.join(f'{xi},{yi}' for xi, yi in zip(x, y)) + ' Z'
        
        shapes.append(dict(
            type='path',
            path=path,
            fillcolor=category_colors[category],
            line=dict(color='rgba(0,0,0,0)'),
            layer='below'
        ))
    
    # Hinzufügen der Trends als Punkte
    for trend in trends:
        # Nehmen wir an, jeder Trend hat genau eine Kategorie
        if trend.categories:
            trend_category = trend.categories[0].name
        else:
            trend_category = 'Kategorie A'  # Standardkategorie, falls keine zugewiesen
        
        # Winkelbereich der Kategorie erhalten
        if trend_category in category_angles:
            start_angle, end_angle = category_angles[trend_category]
        else:
            # Falls die Kategorie nicht definiert ist, setzen wir sie in Kategorie A
            start_angle, end_angle = category_angles['Kategorie A']
        
        # Zufälliger Winkel innerhalb des Kategorie-Segments
        angle = np.random.uniform(start_angle, end_angle)
        angle_rad = deg_to_rad(angle)
        
        # Entfernung vom Zentrum basierend auf der Bedeutung (market_potential)
        radius = trend.market_potential or 5  # Standardwert 5, falls None
        x = radius * np.cos(angle_rad)
        y = radius * np.sin(angle_rad)
        
        # Größe des Punkts basierend auf der Wichtigkeit (relevance)
        point_size = (trend.relevance or 5) * 2  # Skalierungsfaktor 2
        
        # Hinzufügen des Trendpunkts
        data.append(go.Scatter(
            x=[x],
            y=[y],
            mode='markers',
            marker=dict(size=point_size, color='blue'),
            text=[f"<b>{trend.title}</b><br>{trend.description}"],
            hoverinfo='text',
            name=trend.title
        ))
    
    # Achsenbeschriftung hinzufügen
    annotations = []
    for category, (start_angle, end_angle) in category_angles.items():
        angle = (start_angle + end_angle) / 2
        angle_rad = deg_to_rad(angle)
        x = 11 * np.cos(angle_rad)  # Außerhalb des Halbkreises
        y = 11 * np.sin(angle_rad)
        annotations.append(dict(
            x=x,
            y=y,
            text=category,
            showarrow=False,
            font=dict(size=12),
            xanchor='center',
            yanchor='middle'
        ))
    
    # Layout des Diagramms
    layout = go.Layout(
        title='Trend-Radar',
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False, scaleanchor='x', scaleratio=1),
        showlegend=False,
        shapes=shapes,
        annotations=annotations,
        margin=dict(t=50, b=50, l=50, r=50),
        width=800,
        height=400,  # Halbkreis
        hovermode='closest'
    )
    
    fig = go.Figure(data=data, layout=layout)
    return fig