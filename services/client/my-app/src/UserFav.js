// Import React and useState hook from the 'react' package
import React, { useEffect, useState } from 'react';

// Import Link component from 'react-router-dom' package for navigation
import { Link } from 'react-router-dom';

// Import CSS file for styling
import './App.css'; // Import the app.css file

// Import ProfileIcon component
import ProfileIcon from './ProfileIcon';

// Import profile image 
import profileimg from './profileimg.png';

import logo from './logo-1.png';

// Define the UserFav component
function UserFav() {
  // Define state variables using the useState hook
  const [events, setEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetching data from the backend
  useEffect(() => {
    async function fetchData() {
      setIsLoading(true);
      try {
        const response = await fetch(`http://localhost:5001/events_by_favorites`);
        const data = await response.json();
        setEvents(data);
        setIsLoading(false);
      } catch (error) {
        setError(error.message);
        setIsLoading(false);
      }
    }
    fetchData();
  }, []);

  // Highlight matched text
  const createMarkup = (text) => {
    return { __html: text };
  };

  // Return JSX for rendering
  const imageUrl = profileimg;
  return (
    <div className="App">
      {/* Navigation bar */}
      <div className="top-bar">
        <h1>Top Favorite Events</h1>
        {/* Profile icon */}
        <ProfileIcon imageUrl={imageUrl} />
      </div>

      {/* Left bar */}
      <div className="left-bar">
        {/* Logo */}
        <img src={logo} alt="Logo" id="logo1" /> 
        <ul>
          {/* Navigation links */}
          <li><Link to="/events">Events</Link></li>
          <li><Link to="/map">Map</Link></li>
          <li><Link to="/about">People</Link></li>
          <li><Link to="/favorites">Favorites</Link></li>
        </ul>
      </div>

      <div className="events-container">
        <div className="events-list">
          <ul>
            {events.map(event => (
              <li key={event.id} className="event">
                <Link to={`/eventdetail/${event.id}`}>
                  <h3 dangerouslySetInnerHTML={createMarkup(event.name)}></h3>
                </Link>
                <p>Favorites: {event.favorites} </p>
                <p>Description: <span dangerouslySetInnerHTML={createMarkup(event.description)}></span></p>
                <p>Location: {event.location}</p>
                <p>Start Time: {new Date(event.start_time).toLocaleString()}</p>
                <p>End Time: {new Date(event.end_time).toLocaleString()}</p>
                <p>Organization: {event.organization}</p>
                <p>Contact Information: {event.contact_information}</p>
                <p>Registration Link: <a href={event.registration_link}>{event.registration_link}</a></p>
                <p>Keywords: {event.keywords.join(', ')}</p>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

// Export the UserFav component
export default UserFav;
