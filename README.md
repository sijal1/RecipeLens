# RecipeLens

A Django-based recipe application with machine learning capabilities for recipe analysis and recommendations.

## Setup Instructions

1. Create and activate a virtual environment:
```bash
python -m venv myenv
source myenv/Scripts/activate  # On Windows
# OR
source myenv/bin/activate     # On Unix/MacOS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a .env file in the project root with the following content:
```
removed
```

4. Apply database migrations:
```bash
cd src
python manage.py migrate
```

5. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

The application will be available at http://localhost:8000

## Project Structure

- `src/` - Main project directory
  - `RecipeLens/` - Project configuration
  - `main/` - Main application
  - `media/` - User-uploaded files
  - `static/` - Static files (CSS, JS, images)
  - `templates/` - HTML templates

## Features

- Recipe management and storage
- Machine learning-based recipe analysis
- User authentication and authorization
- Media file handling
- Modern UI/UX

## Development

- Use `python manage.py makemigrations` when modifying models
- Run tests with `python manage.py test`
- Static files are collected to `staticfiles/` directory

## Security Notes

- Never commit the .env file
- Keep DEBUG=False in production
- Regularly update dependencies
- Use strong passwords
- Configure proper ALLOWED_HOSTS in production 
