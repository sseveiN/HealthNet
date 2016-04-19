# HealthNet
HealthNet is a website where patients can communicate with doctors and nurses to receive better care.

## Installation
1. Be sure you have Python 3.4, Django 1.9 and SQLite installed
2. Execute `python manage.py makemigrations` in the root directory
3. Execute `python manage.py migrate` in the root directory
4. Create a super user by running `python manage.py createsuperuser`

## Usage
- To start the application simple run `python manage.py runserver` and direct your browser to http://localhost:8000/
- To create an initial Administrator user direct your browser to http://localhost:8000/admin and create an Administrator
    - Be sure to leave is_pending unchecked to be able to use the created Administrator account
    
## Credits
Thanks to https://github.com/dyve/ for use of his django-bootstrap3 form integration.
Thanks to the developers of jQuery, Bootstrap and Fullcalendar.io for use of their products.

Thanks to our core developers:
- Dakota Baber
- Brandon Nieves
- Juliana Kroll
- Tanner Caffery
- Peter Doyle

# Test Liason
If you have any issues during testing, you may contact our test liason Peter Doyle at pxd9796@rit.edu.

## License
You can use this under Apache 2.0. See LICENSE file for details.