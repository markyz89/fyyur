#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://vebuadmin@localhost:5432/fyyur'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODUN: connect to a local postgresql database

from models import *



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)    
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')
  else:
        date = value
        return date

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODUN: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  #data=Venue.query.all()

  data = []
  cities = Venue.query.distinct(Venue.city).all()
  # get all venues
  # loop over cities
  # add venues using query.filter()
  for city in cities:
    data.append(
      {
        "city": city.city,
        "state": city.state,
        "venues": Venue.query.filter(Venue.city == city.city).all()
      }
    )



  return render_template('pages/venues.html', areas=data, );

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODUN: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')

  venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
  data = []

  for venue in venues:
    data.append(
      {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": 0
      }
    )

  response = {
    "count": len(venues),
    "data": data    
  }
  

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODUN: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)
  current_time = datetime.utcnow()

  #number of shows 
  # shows_query = Show.query.filter(venue_id == venue_id).all()

  shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).all()

  upcoming_shows = []
  past_shows = []

  for show in shows_query:
    if(show.start_time > current_time):
      upcoming_shows.append({
        'start_time': show.start_time.isoformat(),
        'artist_name': Artist.query.get(show.artist_id).name,
        'artist_id': Artist.query.get(show.artist_id).id,
      })
    else:
      past_shows.append({
        'start_time': show.start_time.isoformat(),
        'artist_name': Artist.query.get(show.artist_id).name,
        'artist_id': Artist.query.get(show.artist_id).id,
      })

  data = {
    "upcoming_shows": upcoming_shows,
    "past_shows": past_shows,
    "name": venue.name,
    "id" : venue.id,
    "genres": venue.genres,
    "city": venue.city,
    "state": venue.state,
    "address": venue.address,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
  }


  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODUN: insert form data as a new Venue record in the db, instead
  # TODUN: modify data to be the data object returned from db insertion
  form = VenueForm(request.form, meta={'csrf': False})

  if form.validate():
    try: 
      venue = Venue(
        name=form.name.data, 
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        genres=form.genres.data,
        image_link=form.image_link.data,
        website_link=form.website_link.data,
        facebook_link =form.facebook_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data
      )
      db.session.add(venue)
      db.session.commit()
    except:
      print(sys.exc_info)
      flash('Venue was not successfully listed!')
    finally:
        db.session.close()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        # TODUN: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        return render_template('pages/home.html')
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    return render_template('pages/home.html')
    # Thanks Juliano V - Knowledge

  

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # try:
  #   venue = Venue.query.get(venue_id)
  #   db.session.delete(venue)
  #   db.session.commit()
  # except:
  #   db.session.rollback()
  # finally:
  #   db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODUN: replace with real data returned from querying the database 

  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODUN: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')

  artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
  data = []

  for artist in artists:
    data.append(
      {
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": 0
      }
    )

  response = {
    "count": len(artists),
    "data": data    
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODUN: replace with real artist data from the artist table, using artist_id

  data= Artist.query.get(artist_id)

  artist = Artist.query.get(artist_id)
  current_time = datetime.utcnow()

  #number of shows 
  # shows_query = Show.query.filter(artist_id == artist_id).all()

  shows_query = db.session.query(Show).join(Artist).filter(Show.artist_id == artist_id).all()

  upcoming_shows = []
  past_shows = []

  for show in shows_query:
    if(show.start_time > current_time):
      upcoming_shows.append({
        'start_time': show.start_time.isoformat(),
        'venue_name': Venue.query.get(show.venue_id).name,
        'venue_id': Venue.query.get(show.venue_id).id,
      })
    else:
      past_shows.append({
        'start_time': show.start_time.isoformat(),
        'venue_name': Venue.query.get(show.venue_id).name,
        'venue_id': Venue.query.get(show.venue_id).id,
      })

  data = {
    "upcoming_shows": upcoming_shows,
    "past_shows": past_shows,
    "name": artist.name,
    "id" : artist.id,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
  }



  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)



  # TODUN: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODUN: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artist = Artist.query.get(artist_id)
  form = ArtistForm(request.form)


  try:
    artist.name=form.name.data, 
    artist.city=form.city.data,
    artist.state=form.state.data,
    artist.phone=form.phone.data,
    artist.genres=form.genres.data,
    artist.image_link=form.image_link.data,
    artist.website_link=form.website_link.data,
    artist.facebook_link =form.facebook_link.data,
    # artist.seeking_venue=form.seeking_venue.data,
    artist.seeking_description=form.seeking_description.data

    if(form.seeking_venue.data == True):
      artist.seeking_venue=True
    else:
      artist.seeking_venue=False
    

    db.session.commit()
    flash('Artist has been edited!')
  except ValueError as e:
    print(e)
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)


  # TODUN: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODUN: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = Venue.query.get(venue_id)
  form = VenueForm(request.form)

  try:
    venue.name=form.name.data, 
    venue.city=form.city.data,
    venue.state=form.state.data,
    venue.phone=form.phone.data,
    venue.genres=form.genres.data,
    venue.image_link=form.image_link.data,
    venue.website_link=form.website_link.data,
    venue.facebook_link =form.facebook_link.data,
    # venue.seeking_talent=form.seeking_talent.data,
    venue.seeking_description=form.seeking_description.data

    if(form.seeking_talent.data == True):
      venue.seeking_talent=True
    else:
      venue.seeking_talent=False
    

    db.session.commit()
    flash('Venue has been edited!')
  except ValueError as e:
    print(e)
    db.session.rollback()
  finally:
    db.session.close()











  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODUN: insert form data as a new Venue record in the db, instead
  # TODUN: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form, meta={'csrf': False})

  if form.validate():
    try: 
      artist = Artist(
        name=form.name.data, 
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        genres=form.genres.data,
        image_link=form.image_link.data,
        website_link=form.website_link.data,
        facebook_link=form.facebook_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data
      )
      db.session.add(artist)
      db.session.commit()
    except:
      print(sys.exc_info)
      flash('Artist was not successfully listed.')
    finally:
        db.session.close()

        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        # TODUN: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        return render_template('pages/home.html')
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    return render_template('pages/home.html')
    # Thanks Juliano V - Knowledge
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODUN: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  data = []
  shows = Show.query.all()

  for show in shows:
    data.append({
      "venue_id": Venue.query.get(show.venue_id).id,
      "venue_name": Venue.query.get(show.venue_id).name,
      "artist_id": Artist.query.get(show.artist_id).id,
      "artist_name": Artist.query.get(show.artist_id).name,
      "artist_image_link": Artist.query.get(show.artist_id).image_link,
      "start_time": format_datetime(show.start_time)
    })


  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODUN: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)

  try:
    show = Show(
      artist_id=form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data,
    )
    db.session.add(show)
    db.session.commit()
  except:
    print(sys.exc_info)
    flash('Show was not successfully listed!')
  finally:
    db.session.close()

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODUN: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
