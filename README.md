
# BlogSite

**BlogSite** is a Django-based web application where users can view and rate blogs. Ratings are collected and processed using Django and Celery.

## Features

- **Blog Creation**: Blogs can be created and managed via the Django admin panel.
- **User Ratings**: Users can rate blogs, and their ratings are aggregated using Celery for efficient background processing.
- **Rating Bins**: Ratings are grouped and averaged using `RatingBin` records for performance optimization.

## Requirements

- Django
- Celery
- Redis (for Celery message brokering)

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/MohammadSafaeii/blogPost.git
   cd blogPost
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Django migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Start the Django server**:
   ```bash
   python manage.py runserver
   ```

5. **Start Celery worker**:
   ```bash
   celery -A blogSite worker -l info
   ```

6. **Start Celery beat (for scheduled tasks)**:
   ```bash
   celery -A blogSite beat -l info
   ```

## Documentation

- For information about detecting anomalous data, check out the PDF documentation located in the docs/ folder.

## Additional Information

- **Rating System**: Ratings are calculated using a scheduled Celery task that processes ratings every day.
- **Database**: All blog and rating data are stored in a relational database, with background task management handled by Celery.
