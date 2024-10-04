from .extensions import db

# Assoziationstabelle für die Many-to-Many-Beziehung
trend_categories = db.Table('trend_categories',
    db.Column('trend_id', db.Integer, db.ForeignKey('trend.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    trends = db.relationship('Trend', secondary=trend_categories, back_populates='categories')

    def __repr__(self):
        return f"<Category {self.name}>"

class Trend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    phase = db.Column(db.String(50), nullable=False)
    time_horizon = db.Column(db.String(50), nullable=False)
    
    relevance = db.Column(db.Integer, nullable=False)
    market_potential = db.Column(db.Integer, nullable=False)
    likelihood = db.Column(db.Integer, nullable=False)
    sustainability = db.Column(db.Integer, nullable=False)
    maturity_level = db.Column(db.Integer, nullable=False)

    categories = db.relationship('Category', secondary=trend_categories, back_populates='trends')

    def __repr__(self):
        return f"<Trend {self.title}>"

# Zeithorizonte und Phasen definieren
time_horizons = ['Short-term', 'Mid-term', 'Long-term']
phases = ['Park', 'Wait & See', 'Observe', 'Be Prepared', 'Act Now']

# Map Zeithorizonte zu Radien
time_horizon_radii = {
    'Short-term': 1,
    'Mid-term': 2,
    'Long-term': 3
}

def get_category_angles():
    categories = Category.query.order_by(Category.id).all()
    num_categories = len(categories)
    angle_step = 360 / num_categories if num_categories > 0 else 0
    category_angles = {}
    for i, category in enumerate(categories):
        category_angles[category.name] = i * angle_step
    return category_angles

def init_categories():
    existing_categories = Category.query.all()
    if not existing_categories:
        category_names = ['Produkte', 'Service', 'Prozesse', 'Staff', 'Supply', 'Technology']
        for name in category_names:
            category = Category(name=name)
            db.session.add(category)
        db.session.commit()