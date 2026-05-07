"""
Context processors to inject variables into all templates.
"""

from flask import request
from app.models.category import Category


def utility_processor():
    """Inject utility functions and data into all templates."""
    
    def get_categories():
        """Get all categories for navigation."""
        return Category.query.order_by(Category.name).limit(5).all()
    
    def moment():
        """Provide moment-like functionality for dates."""
        from datetime import datetime
        
        class Moment:
            @staticmethod
            def year():
                return datetime.utcnow().year
        
        return Moment()
    
    return dict(
        get_categories=get_categories,
        moment=moment
    )